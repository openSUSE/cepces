import typing as t
from _typeshed import Incomplete
from gssapi import names as names
from gssapi._utils import import_gssapi_extension as import_gssapi_extension
from gssapi.raw import (
    creds as rcreds,
    named_tuples as tuples,
    names as rnames,
    oids as roids,
)

rcred_imp_exp: Incomplete
rcred_s4u: Incomplete
rcred_cred_store: Incomplete
rcred_rfc5588: Incomplete

class Credentials(rcreds.Creds):
    def __new__(
        cls,
        base: rcreds.Creds | None = None,
        token: bytes | None = None,
        name: rnames.Name | None = None,
        lifetime: int | None = None,
        mechs: t.Iterable[roids.OID] | None = None,
        usage: str = "both",
        store: dict[bytes | str, bytes | str] | None = None,
    ) -> Credentials: ...
    @property
    def name(self) -> names.Name: ...
    @property
    def lifetime(self) -> int: ...
    @property
    def mechs(self) -> set[roids.OID]: ...
    @property
    def usage(self) -> str: ...
    @classmethod
    def acquire(
        cls,
        name: rnames.Name | None = None,
        lifetime: int | None = None,
        mechs: t.Iterable[roids.OID] | None = None,
        usage: str = "both",
        store: dict[bytes | str, bytes | str] | None = None,
    ) -> tuples.AcquireCredResult: ...
    def store(
        self,
        store: dict[bytes | str, bytes | str] | None = None,
        usage: str = "both",
        mech: roids.OID | None = None,
        overwrite: bool = False,
        set_default: bool = False,
    ) -> tuples.StoreCredResult: ...
    def impersonate(
        self,
        name: rnames.Name | None = None,
        lifetime: int | None = None,
        mechs: t.Iterable[roids.OID] | None = None,
        usage: str = "initiate",
    ) -> Credentials: ...
    def inquire(
        self,
        name: bool = True,
        lifetime: bool = True,
        usage: bool = True,
        mechs: bool = True,
    ) -> tuples.InquireCredResult: ...
    def inquire_by_mech(
        self,
        mech: roids.OID,
        name: bool = True,
        init_lifetime: bool = True,
        accept_lifetime: bool = True,
        usage: bool = True,
    ) -> tuples.InquireCredByMechResult: ...
    def add(
        self,
        name: rnames.Name,
        mech: roids.OID,
        usage: str = "both",
        init_lifetime: int | None = None,
        accept_lifetime: int | None = None,
        impersonator: rcreds.Creds | None = None,
        store: dict[bytes | str, bytes | str] | None = None,
    ) -> Credentials: ...
    def export(self) -> bytes: ...
    def __reduce__(self) -> tuple[type["Credentials"], tuple[None, bytes]]: ...
