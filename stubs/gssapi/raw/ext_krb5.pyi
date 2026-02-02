import _cython_3_2_4limitednofinalize
import gssapi.raw.types as gsstypes
from _typeshed import Incomplete
from gssapi.raw.misc import GSSError as GSSError
from gssapi.raw.named_tuples import CfxKeyData as CfxKeyData, Rfc1964KeyData as Rfc1964KeyData

GSSAPI: str
__reduce_cython__: _cython_3_2_4limitednofinalize.cython_function_or_method
__setstate_cython__: _cython_3_2_4limitednofinalize.cython_function_or_method
__test__: dict
krb5_ccache_name: _cython_3_2_4limitednofinalize.cython_function_or_method
krb5_export_lucid_sec_context: _cython_3_2_4limitednofinalize.cython_function_or_method
krb5_extract_authtime_from_sec_context: _cython_3_2_4limitednofinalize.cython_function_or_method
krb5_extract_authz_data_from_sec_context: _cython_3_2_4limitednofinalize.cython_function_or_method
krb5_get_tkt_flags: _cython_3_2_4limitednofinalize.cython_function_or_method
krb5_import_cred: _cython_3_2_4limitednofinalize.cython_function_or_method
krb5_set_allowable_enctypes: _cython_3_2_4limitednofinalize.cython_function_or_method

class Krb5LucidContext:
    @classmethod
    def __init__(cls, *args, **kwargs) -> None: ...
    def __reduce__(self): ...

class Krb5LucidContextV1(Krb5LucidContext):
    cfx_kd: Incomplete
    endtime: Incomplete
    is_initiator: Incomplete
    protocol: Incomplete
    recv_seq: Incomplete
    rfc1964_kd: Incomplete
    send_seq: Incomplete
    version: Incomplete
    @classmethod
    def __init__(cls, *args, **kwargs) -> None: ...
    def __reduce__(self): ...
