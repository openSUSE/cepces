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
# pylint: disable=too-many-arguments
"""This module contains wrapper classes for the Kerberos integration."""

import ctypes
import re
from typing import Any
from cepces import Base as CoreBase
from cepces.krb5 import types as ktypes
from cepces.krb5 import functions as kfuncs

# Regular expressions for matching against keytab and principal names.
NAME_EX = r"^(?:(?P<type>[A-Z]+):)?(?P<residual>.+)$"
PRINCIPAL_EX = r"^(?P<primary>[^/]+)(?:/(?P<instance>.+))?@(?P<realm>.+)$"


class Base(CoreBase):
    """Base class for any Kerberos wrapper class."""

    def __init__(self, handle: Any) -> None:
        super().__init__()

        self._logger.debug("Handle %s", handle)
        self._handle = handle

    @property
    def handle(self) -> Any:
        """Get the Kerberos context handle."""
        if hasattr(self, "_handle"):
            return self._handle

        return None


class Context(Base):
    """Represents the Kerberos context."""

    def __init__(self):
        super().__init__(ktypes.krb5_context())

        kfuncs.init_context(self.handle)

    def __del__(self):
        if self.handle:
            # self._logger.debug("Freeing context {}".format(self.handle))
            kfuncs.free_context(self.handle)


class PrincipalName(Base):
    """Representation of a Kerberos Principal Name.

    It consists of one or more principal name components, separated by slashes,
    optionally followed by the @ character and a realm name. If the realm name
    is not specified, the local realm is used.
    """

    def __init__(
        self,
        principal: "Principal",
        name: str | None,
        context: "Context",
        host: bytes | None,
        service: bytes | None,
        service_type: int | None,
    ) -> None:
        super().__init__(None)

        if name:
            kfuncs.parse_name(
                context.handle,
                name.encode("utf-8"),
                principal.handle,
            )
        else:
            kfuncs.sname_to_principal(
                context.handle,
                host,
                service,
                ktypes.PrincipalType.KRB5_NT_SRV_HST
                if service_type is None
                else service_type,
                principal.handle,
            )

        # Unparse the recently acquired principal to retrieve the different
        # components.
        buffer = ctypes.c_char_p()
        kfuncs.unparse_name(context.handle, principal.handle, buffer)
        if buffer.value is None:
            raise ValueError("Failed to unparse principal name")
        name = buffer.value.decode("utf-8")
        kfuncs.free_unparsed_name(context.handle, buffer)

        match = re.match(PRINCIPAL_EX, name)
        if match is None:
            raise ValueError(f"Invalid principal format: {name}")

        primary = match.group("primary")
        realm = match.group("realm")
        if primary is None or realm is None:
            raise ValueError(f"Invalid principal format: {name}")

        self._primary: str = primary
        self._realm: str = realm

        raw_instance = match.group("instance")
        if raw_instance and "/" in raw_instance:
            parts = raw_instance.split("/", 1)
            self._instance: str | None = parts[0]
            self._domain: str | None = parts[1]
        else:
            self._instance = raw_instance
            self._domain = None

        if service_type is not None:
            self._service_type: int = service_type
        elif self._domain is not None:
            self._service_type = ktypes.PrincipalType.KRB5_NT_SRV_HST_DOMAIN
        elif self._instance is not None:
            self._service_type = ktypes.PrincipalType.KRB5_NT_SRV_HST
        else:
            self._service_type = (
                ktypes.PrincipalType.KRB5_NT_ENTERPRISE_PRINCIPAL
            )

    @property
    def primary(self) -> str:
        """Get the primary component of the name."""
        return self._primary

    @property
    def instance(self) -> str | None:
        """Get the instance component of the name."""
        return self._instance

    @property
    def domain(self) -> str | None:
        """Get the domain component of a domain-based service name."""
        return self._domain

    @property
    def realm(self) -> str:
        """Get the realm component of the name."""
        return self._realm

    @property
    def service_type(self) -> int:
        """Get the principal type."""
        return self._service_type


class Principal(Base):
    """Representation of a Kerberos Principal."""

    def __init__(
        self,
        context: "Context",
        name: str | None = None,
        host: bytes | None = None,
        service: bytes | None = None,
        service_type: int | None = None,
    ) -> None:
        super().__init__(ktypes.krb5_principal())

        self._context: Context = context
        self._name: PrincipalName = PrincipalName(
            self,
            name,
            context,
            host,
            service,
            service_type,
        )

    def __del__(self):
        if self.handle:
            # self._logger.debug("Freeing principal {}".format(self.handle))
            kfuncs.free_principal(self._context.handle, self.handle)

    def __str__(self) -> str:
        if self._name.domain:
            return "%s/%s/%s@%s" % (
                self._name.primary,
                self._name.instance,
                self._name.domain,
                self._name.realm,
            )
        if self._name.instance:
            return "%s/%s@%s" % (
                self._name.primary,
                self._name.instance,
                self._name.realm,
            )
        return "%s@%s" % (self._name.primary, self._name.realm)

    @property
    def primary(self) -> str:
        """Get the primary component of the name."""
        return self._name.primary

    @property
    def instance(self) -> str | None:
        """Get the instance component of the name."""
        return self._name.instance

    @property
    def domain(self) -> str | None:
        """Get the domain component of a domain-based service name."""
        return self._name.domain

    @property
    def realm(self) -> str:
        """Get the realm component of the name."""
        return self._name.realm

    @property
    def service_type(self) -> int:
        """Get the principal type."""
        return self._name.service_type


def get_default_keytab_name() -> str:
    """Get the default keytab name.

    Returns:
        str: The default keytab name.
    """
    context = Context()
    buffer = ctypes.create_string_buffer(ktypes.LINE_MAX)
    kfuncs.kt_default_name(context.handle, buffer, ktypes.LINE_MAX)
    return buffer.value.decode("utf-8")
