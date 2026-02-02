import gssapi
from gssapi.raw.oids import OID as OID
from gssapi.raw.types import RequirementFlag as RequirementFlag
from typing import NamedTuple

class AcquireCredResult(NamedTuple):
    creds: gssapi.raw.creds.Creds
    mechs: set[OID]
    lifetime: int

class InquireCredResult(NamedTuple):
    name: gssapi.raw.names.Name | None
    lifetime: int | None
    usage: str | None
    mechs: set[OID] | None

class InquireCredByMechResult(NamedTuple):
    name: gssapi.raw.names.Name | None
    init_lifetime: int | None
    accept_lifetime: int | None
    usage: str | None

class AddCredResult(NamedTuple):
    creds: gssapi.raw.creds.Creds | None
    mechs: set[OID]
    init_lifetime: int
    accept_lifetime: int

class DisplayNameResult(NamedTuple):
    name: bytes
    name_type: OID | None

class WrapResult(NamedTuple):
    message: bytes
    encrypted: bool

class UnwrapResult(NamedTuple):
    message: bytes
    encrypted: bool
    qop: int

class AcceptSecContextResult(NamedTuple):
    context: gssapi.raw.sec_contexts.SecurityContext
    initiator_name: gssapi.raw.names.Name
    mech: OID
    token: bytes | None
    flags: RequirementFlag
    lifetime: int
    delegated_creds: gssapi.raw.creds.Creds | None
    more_steps: bool

class InitSecContextResult(NamedTuple):
    context: gssapi.raw.sec_contexts.SecurityContext
    mech: OID
    flags: RequirementFlag
    token: bytes | None
    lifetime: int
    more_steps: bool

class InquireContextResult(NamedTuple):
    initiator_name: gssapi.raw.names.Name | None
    target_name: gssapi.raw.names.Name | None
    lifetime: int | None
    mech: OID | None
    flags: RequirementFlag | None
    locally_init: bool | None
    complete: bool | None

class StoreCredResult(NamedTuple):
    mechs: list[OID]
    usage: str

class IOVUnwrapResult(NamedTuple):
    encrypted: bool
    qop: int

class InquireNameResult(NamedTuple):
    attrs: list[bytes]
    is_mech_name: bool
    mech: OID

class GetNameAttributeResult(NamedTuple):
    values: list[bytes]
    display_values: list[bytes]
    authenticated: bool
    complete: bool

class InquireAttrsResult(NamedTuple):
    mech_attrs: set[OID]
    known_mech_attrs: set[OID]

class DisplayAttrResult(NamedTuple):
    name: bytes
    short_desc: bytes
    long_desc: bytes

class InquireSASLNameResult(NamedTuple):
    sasl_mech_name: bytes
    mech_name: bytes
    mech_description: bytes

class Rfc1964KeyData(NamedTuple):
    sign_alg: int
    seal_alg: int
    key_type: int
    key: bytes

class CfxKeyData(NamedTuple):
    ctx_key_type: int
    ctx_key: bytes
    acceptor_subkey_type: int | None
    acceptor_subkey: bytes | None
