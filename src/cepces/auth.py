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
import os
import subprocess
import keyring
from keyring.errors import KeyringLocked, KeyringError
from cepces import Base
from cepces.krb5.functions import Error as KerberosError
from cepces.krb5.types import EncryptionType as KerberosEncryptionType
from cepces.soap import auth as SOAPAuth


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
        ccache = section.get("ccache", True)
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
            except KerberosError:
                # Ignore
                pass

            if auth:
                return auth

        raise RuntimeError("No suitable key found in keytab.")


class UsernamePasswordAuthenticationHandler(AuthenticationHandler):
    """Handler for Username and Password based authentication."""

    def prompt_credentials(self) -> tuple[str, str]:
        """Asks interactively for credentials to store in keyring."""
        try:
            env = os.environ.copy()
            env.setdefault("DISPLAY", ":0")
            result = subprocess.run(
                args=["zenity",
                      "--username",
                      "--password",
                      "--text=Enter your username and password",
                      "--title=Login credentials"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                env=env,
            )
            credentials = result.stdout.strip().split('|', 1)
            if len(credentials) != 2:
                return None, None
            return credentials[0], credentials[1]
        except subprocess.CalledProcessError:
            return None, None

    def handle(self):
        parser = self._parser

        # Ensure there's a usernamepassword section present.
        if "usernamepassword" not in parser:
            raise RuntimeError(
                'Missing "usernamepassword" section in configuration.',
            )

        section = parser['usernamepassword']

        keyring_service = section.get('keyring_service', "cepces")
        username = section.get('username', None)
        password = section.get('password', None)

        try:
            keyring_password = keyring.get_password(keyring_service, username)
            if keyring_password:
                password = keyring_password
            if not username or not password:
                username, password = self.prompt_credentials()
                try:
                    keyring.set_password(keyring_service, username, password)
                except KeyringLocked as e:
                    raise RuntimeError(
                        'Keyring locked. Can not unlock.',
                    ) from e
                except KeyringError as e:
                    raise RuntimeError(
                        'Can not set credentials in default keyring for service {keyring_service}',
                    ) from e
        except KeyringLocked as e:
            raise RuntimeError(
                'Keyring locked. Can not unlock.',
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
