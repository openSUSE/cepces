# -*- coding: utf-8 -*-
#
# This file is part of cepces.
#
# cepces is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# cepces is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with cepces.  If not, see <http://www.gnu.org/licenses/>.
#
"""Module containing authentication type handlers."""
from abc import ABCMeta, abstractmethod
from cepces import Base
from cepces.credentials import CredentialsHandler
from cepces.keyring import KeyringHandler, KeyringOperationError
from cepces.krb5.types import EncryptionType as KerberosEncryptionType
from cepces.soap import auth as SOAPAuth
import gssapi.exceptions


def strtobool(value):
    if str(value).lower() in ("t", "true", "y", "yes", "1"):
        return True
    return False


class AuthenticationHandler(Base, metaclass=ABCMeta):
    """Base class for any authentication handled."""

    def __init__(self, parser):
        super().__init__()
        self._parser = parser

    @abstractmethod
    def handle(self):
        """Constructs and returns a SOAPAuth authentication handler."""


class AnonymousAuthenticationHandler(AuthenticationHandler):
    """Constructs an anonymous authentication handler."""

    def handle(self):
        return SOAPAuth.AnonymousAuthentication()


class KerberosAuthenticationHandler(AuthenticationHandler):
    """Kerberos Authentication Handler"""

    def handle(self):
        parser = self._parser

        # Ensure there's a kerberos section present.
        if "kerberos" not in parser:
            raise RuntimeError('Missing "kerberos" section in configuration.')

        section = parser["kerberos"]

        keytab = section.get("keytab", None)
        realm = section.get("realm", None)
        ccache = strtobool(section.get("ccache", True))
        principals = section.get("principals", "")
        enctypes = section.get("enctypes", "")
        delegate = strtobool(section.get("delegate", True))

        # Decode all encryption types.
        etypes = []

        for enctype in enctypes.strip().split("\n"):
            etype = "KRB5_ENCTYPE_{}".format(enctype.replace("-", "_").upper())

            try:
                etypes.append(KerberosEncryptionType[etype])
            except KeyError as e:
                raise RuntimeError(
                    "Unknown encryption type: {}".format(enctype),
                ) from e

        # Figure out which principal to use.
        auth = None

        for principal in principals.strip().split("\n"):
            if realm:
                principal = "{}@{}".format(principal, realm)

            try:
                auth = SOAPAuth.TransportKerberosAuthentication(
                    principal_name=principal,
                    init_ccache=ccache,
                    keytab=keytab,
                    delegate=delegate,
                )
            except gssapi.exceptions.GSSError as e:
                # Log the error and continue trying other principals
                self._logger.warning(
                    "GSSError for principal %s: %s", principal, e
                )
                continue

            # On success, check if auth is valid and then leave
            if auth:
                self._logger.info(
                    "Successfully authenticated with principal %s", principal
                )
                return auth

        raise RuntimeError("No suitable key found in keytab.")


class UsernamePasswordAuthenticationHandler(AuthenticationHandler):
    """Handler for Username and Password based authentication."""

    def prompt_credentials(self) -> tuple[str, str]:
        """Asks interactively for credentials to store in keyring."""
        credentials_handler = CredentialsHandler(title="Login credentials")
        if not credentials_handler.is_supported():
            self._logger.error(
                "Cannot prompt for credentials: "
                "pinentry utility is not available"
            )
            return None, None

        username, password = credentials_handler.prompt_credentials(
            username_description="Enter your username",
            password_description="Enter your password",
        )
        return username, password

    def handle(self):
        parser = self._parser

        # Ensure there's a usernamepassword section present.
        if "usernamepassword" not in parser:
            raise RuntimeError(
                'Missing "usernamepassword" section in configuration.',
            )

        section = parser["usernamepassword"]

        keyring_service = section.get("keyring_service", "cepces")
        username = section.get("username", None)
        password = section.get("password", None)

        # Initialize keyring handler
        keyring = KeyringHandler(keyring_service)

        # Check if keyring is supported and try to get password from it
        if keyring.is_supported():
            keyctl_password = keyring.get_password(username)
            if keyctl_password:
                password = keyctl_password
        else:
            self._logger.warning(
                "Kernel keyring is not supported on this system. "
                "Credentials will not be stored."
            )

        # If credentials are missing, prompt for them
        if not username or not password:
            username, password = self.prompt_credentials()
            # Store credentials in kernel keyring if supported
            if keyring.is_supported():
                try:
                    keyring.set_password(username, password)
                except KeyringOperationError as e:
                    raise RuntimeError(
                        f"Failed to store credentials in kernel keyring for "
                        f"service {keyring_service}: {e}",
                    ) from e

        return SOAPAuth.MessageUsernamePasswordAuthentication(
            username,
            password,
        )


class CertificateAuthenticationHandler(AuthenticationHandler):
    """Handler for Certificate based authentication."""

    def handle(self):
        """Constructs and returns a SOAPAuth authentication handler."""
        parser = self._parser

        # Ensure there's a certificate section present.
        if "certificate" not in parser:
            raise RuntimeError(
                'Missing "certificate" section in configuration.',
            )

        section = parser["certificate"]

        certfile = section.get("certfile", None)
        keyfile = section.get("keyfile", None)

        return SOAPAuth.TransportCertificateAuthentication(
            certfile,
            keyfile,
        )
