from _typeshed import Incomplete
from gssapi import _utils
from gssapi.creds import Credentials as Credentials
from gssapi.names import Name as Name
from gssapi.raw import (
    chan_bindings as rchan_bindings,
    named_tuples as tuples,
    names as rnames,
    oids as roids,
    sec_contexts as rsec_contexts,
)
from gssapi.raw.types import (
    IntEnumFlagSet as IntEnumFlagSet,
    RequirementFlag as RequirementFlag,
)

class SecurityContext(
    rsec_contexts.SecurityContext, metaclass=_utils.CheckLastError
):
    def __new__(
        cls,
        base: rsec_contexts.SecurityContext | None = None,
        token: bytes | None = None,
        name: rnames.Name | None = None,
        creds: Credentials | None = None,
        lifetime: int | None = None,
        flags: int | None = None,
        mech: roids.OID | None = None,
        channel_bindings: rchan_bindings.ChannelBindings | None = None,
        usage: str | None = None,
    ) -> SecurityContext: ...
    usage: Incomplete
    def __init__(
        self,
        base: rsec_contexts.SecurityContext | None = None,
        token: bytes | None = None,
        name: rnames.Name | None = None,
        creds: Credentials | None = None,
        lifetime: int | None = None,
        flags: int | None = None,
        mech: roids.OID | None = None,
        channel_bindings: rchan_bindings.ChannelBindings | None = None,
        usage: str | None = None,
    ) -> None: ...
    def get_signature(self, message: bytes) -> bytes: ...
    def verify_signature(self, message: bytes, mic: bytes) -> int: ...
    def wrap(self, message: bytes, encrypt: bool) -> tuples.WrapResult: ...
    def unwrap(self, message: bytes) -> tuples.UnwrapResult: ...
    def encrypt(self, message: bytes) -> bytes: ...
    def decrypt(self, message: bytes) -> bytes: ...
    def get_wrap_size_limit(
        self, desired_output_size: int, encrypted: bool = True
    ) -> int: ...
    def process_token(self, token: bytes) -> None: ...
    def export(self) -> bytes: ...
    @property
    def lifetime(self) -> int: ...
    @property
    def delegated_creds(self) -> Credentials | None: ...
    initiator_name: Incomplete
    target_name: Incomplete
    mech: Incomplete
    actual_flags: Incomplete
    locally_initiated: Incomplete
    @property
    @_utils.check_last_err
    def complete(self) -> bool: ...
    @_utils.catch_and_return_token
    def step(self, token: bytes | None = None) -> bytes | None: ...
    def __reduce__(
        self,
    ) -> tuple[type["SecurityContext"], tuple[None, bytes]]: ...
