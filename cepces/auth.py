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
from cepces.krb5.functions import Error as KerberosError
from cepces.krb5.types import EncryptionType as KerberosEncryptionType
from cepces.soap import auth as SOAPAuth


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
        if 'kerberos' not in parser:
            raise RuntimeError('Missing "kerberos" section in configuration.')

        section = parser['kerberos']

        keytab = section.get('keytab', None)
        realm = section.get('realm', None)
        ccache = section.get('ccache', True)
        principals = section.get('principals', '')
        enctypes = section.get('enctypes', '')

        # Decode all encryption types.
        etypes = []

        for enctype in enctypes.strip().split('\n'):
            etype = "KRB5_ENCTYPE_{}".format(enctype.replace('-', '_').upper())

            try:
                etypes.append(KerberosEncryptionType[etype])
            except KeyError as e:
                raise RuntimeError(
                    'Unknown encryption type: {}'.format(enctype),
                ) from e

        # Figure out which principal to use.
        auth = None

        for principal in principals.strip().split('\n'):
            if realm:
                principal = '{}@{}'.format(principal, realm)

            try:
                auth = SOAPAuth.TransportKerberosAuthentication(
                    principal_name=principal,
                    init_ccache=ccache,
                    keytab=keytab,
                )
            except KerberosError:
                # Ignore
                pass

        if auth:
            return auth
        else:
            raise RuntimeError('No suitable key found in keytab.')


class UsernamePasswordAuthenticationHandler(AuthenticationHandler):
    """Handler for Username and Password based authentication."""
    def handle(self):
        parser = self._parser

        # Ensure there's a usernamepassword section present.
        if 'usernamepassword' not in parser:
            raise RuntimeError(
                'Missing "usernamepassword" section in configuration.',
            )

        section = parser['usernamepassword']

        username = section.get('username', None)
        password = section.get('password', None)

        return SOAPAuth.MessageUsernamePasswordAuthentication(
            username,
            password,
        )


class CertificateAuthenticationHandler(AuthenticationHandler):
    """Handler for Certificate based authentication."""
    def handle(self):
        """Constructs and returns a SOAPAuth authentication handler."""
        raise NotImplementedError()
