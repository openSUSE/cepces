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
import base64
import hashlib
import os
from datetime import datetime
import gssapi
from requests_gssapi import HTTPSPNEGOAuth
from cepces import Base
from cepces.krb5 import types as ktypes
from cepces.krb5.core import Context, Principal
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

    def __init__(
        self,
        principal_name=None,
        init_ccache=True,
        keytab=None,
        enctypes=None,
        delegate=True,
    ):
        super().__init__()

        self._config = {}
        self._config["name"] = principal_name
        self._config["init_ccache"] = init_ccache
        self._config["keytab"] = keytab
        self._config["enctypes"] = enctypes
        self._config["delegate"] = delegate

        context = Context()

        # Create a valid principal using default realm if none is specified
        principal = Principal(
            context,
            name=self._config["name"],
            service_type=ktypes.PrincipalType.KRB5_NT_ENTERPRISE_PRINCIPAL,
        )
        self._config["principal"] = "%s@%s" % (
            principal.primary,
            principal.realm,
        )

        # Only initialize a credential cache if requested. Otherwise, rely on
        # a credential cache already being available.
        gssapi_cred = None
        if self._config["init_ccache"]:
            gssapi_cred = self._init_ccache()

        self._init_transport(gssapi_cred)

    def _init_ccache(self):
        krb5_mech = gssapi.OID.from_int_seq("1.2.840.113554.1.2.2")
        gss_name = gssapi.Name(self._config["principal"], gssapi.NameType.user)

        os.environ["KRB5CCNAME"] = "MEMORY:cepces"

        gssapi_cred = gssapi.raw.acquire_cred_from(
            store={
                b"client_keytab": self._config["keytab"],
                # This doesn't work, we need to set KRB5CCNAME
                # b"ccache": "MEMORY:cepces",
            },
            name=gss_name,
            mechs=[krb5_mech],
            usage="initiate",
        )

        return gssapi_cred

    def _init_transport(self, gssapi_cred=None):
        gss_name = gssapi.Name(self._config["principal"], gssapi.NameType.user)

        creds = gssapi.Credentials(
            base=gssapi_cred.creds, name=gss_name, usage="initiate"
        )

        self._transport = HTTPSPNEGOAuth(
            creds=creds,
            delegate=self._config["delegate"],
            mech=gssapi.mechs.Mechanism.from_sasl_name("SPNEGO"),
            channel_bindings="tls-server-end-point",
        )

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
        self._username: str = username
        self._password: str = password
        self._init_digest()

    def _init_digest(self):
        self._created = datetime.now()
        raw_nonce = f"{self._username}:{self._password}:{self._created}"
        self._nonce = hashlib.md5(raw_nonce.encode("utf-8")).digest()

        # m = hashlib.sha1()
        # m.update(self._nonce)
        # m.update(self._created.strftime("%Y-%m-%dT%H:%M:%SZ").encode("utf-8"))
        # m.update(self._password.encode("utf-8"))
        # self._password = base64.b64encode(m.digest()).decode("utf-8")

        self._nonce = base64.b64encode(self._nonce).decode("utf-8")

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
        # envelope.header.security.usernametoken.password = self._password_digest
        envelope.header.security.usernametoken.nonce = self._nonce
        envelope.header.security.usernametoken.created = self._created

        return envelope


class TransportCertificateAuthentication(Authentication):
    """Transport authentication using a client certificate."""

    def __init__(self, certfile, keyfile):
        super().__init__()
        self._certfile = certfile
        self._keyfile = keyfile

    @property
    def transport(self):
        return None

    @property
    def clientcertificate(self):
        return (self._certfile, self._keyfile)

    def post_process(self, envelope):
        # Nothing to be done here.
        return envelope
