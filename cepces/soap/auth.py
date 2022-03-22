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
# This module contains SOAP related classes, implementing a loose subset of the
# specification, just enough to be able to communicate a service.
#
"""This module contains SOAP related authentication."""
from abc import ABCMeta, abstractmethod, abstractproperty
import os
from requests_kerberos import HTTPKerberosAuth
from cepces import Base
from cepces.krb5 import types as ktypes
from cepces.krb5.core import Context, Keytab, Principal
from cepces.krb5.core import CredentialOptions, Credentials, CredentialCache
from cepces.soap.types import Security as WSSecurity, UsernameToken


class Authentication(Base, metaclass=ABCMeta):
    """Base class for handling authentication of SOAP endpoints."""
    @abstractproperty
    def transport(self):
        """Property containing authentication mechanism for the transport layer
        (i.e. requests)."""

    @abstractproperty
    def clientcertificate(self):
        """Property containing TLS client certificate ínformation for the transport layer
        (i.e. requests)."""

    @abstractmethod
    def post_process(self, envelope):
        """Method for securing (post processing) a SOAP envelope."""


class AnonymousAuthentication(Authentication):
    """A simple pass-through authentication method."""
    @property
    def transport(self):
        """Property containing authentication mechanism for the transport layer
        (i.e. requests)."""
        return None

    def post_process(self, envelope):
        # Nothing to be done here.
        return envelope


class TransportKerberosAuthentication(Authentication):
    """Kerberos authentication on the transport level."""
    def __init__(self, principal_name=None, init_ccache=True, keytab=None,
                 enctypes=None):
        super().__init__()

        self._config = {}
        self._config['name'] = principal_name
        self._config['init_ccache'] = init_ccache
        self._config['keytab'] = keytab
        self._config['enctypes'] = enctypes

        # Only initialize a credential cache if requested. Otherwise, rely on
        # a credential cache already being available.
        if self._config['init_ccache']:
            self._init_ccache()

        self._init_transport()

    def _init_ccache(self):
        start_time = 0

        context = Context()
        keytab = Keytab(context, keytab=self._config['keytab'])
        principal = Principal(
            context,
            name=self._config['name'],
            service_type=ktypes.PrincipalType.KRB5_NT_SRV_HST,
        )
        credential_options = CredentialOptions(context)
        credential_options.forwardable = True
        credential_options.encryption_types = self._config['enctypes']

        tkt_service = '{service}/{host}@{realm}'.format(
            service=ktypes.KRB5_TGS_NAME,
            host=principal.realm,
            realm=principal.realm,
        )

        credentials = Credentials(
            context,
            principal,
            keytab,
            start_time,
            tkt_service,
            credential_options,
        )

        ccache_name = "MEMORY:cepces"
        self._ccache = CredentialCache(
            context,
            ccache_name,
            principal,
            credentials,
        )

        os.environ["KRB5CCNAME"] = ccache_name

    def _init_transport(self):
        self._transport = HTTPKerberosAuth(principal=self._config['name'],
                                           delegate=True)

    @property
    def transport(self):
        return self._transport

    @property
    def clientcertificate(self):
        return None

    def post_process(self, envelope):
        # Nothing to be done here.
        return envelope


class MessageUsernamePasswordAuthentication(Authentication):
    """Message authentication using a username and a password."""
    def __init__(self, username, password):
        super().__init__()
        self._username = username
        self._password = password

    @property
    def transport(self):
        return None

    @property
    def clientcertificate(self):
        return None

    def post_process(self, envelope):
        envelope.header.element.append(WSSecurity.create())

        envelope.header.security.element.append(UsernameToken.create())
        envelope.header.security.usernametoken.username = self._username
        envelope.header.security.usernametoken.password = self._password

        return envelope


class TransportCertificateAuthentication(Authentication):
    """Transport authentication using a client certificate."""
    def __init__(self, certfile, keyfile):
        super().__init__()
        self._certfile = certfile
        self._keyfile = keyfile
        os.system('echo DEBUG Certificate file: ""%s"" Key file ""%s"" >> /var/log/cepces/cepces.log' % ( certfile, keyfile ))

    @property
    def transport(self):
        return None

    @property
    def clientcertificate(self):
        return ( self._certfile, self._keyfile )

    def post_process(self, envelope):
        # Nothing to be done here.
        return envelope
