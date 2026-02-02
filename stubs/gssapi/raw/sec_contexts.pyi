import _cython_3_2_4limitednofinalize
from gssapi.raw.misc import GSSError as GSSError
from gssapi.raw.named_tuples import (
    AcceptSecContextResult as AcceptSecContextResult,
    InitSecContextResult as InitSecContextResult,
    InquireContextResult as InquireContextResult,
)
from gssapi.raw.types import (
    IntEnumFlagSet as IntEnumFlagSet,
    MechType as MechType,
    RequirementFlag as RequirementFlag,
)

GSSAPI: str
__reduce_cython__: _cython_3_2_4limitednofinalize.cython_function_or_method
__setstate_cython__: _cython_3_2_4limitednofinalize.cython_function_or_method
__test__: dict
accept_sec_context: _cython_3_2_4limitednofinalize.cython_function_or_method
context_time: _cython_3_2_4limitednofinalize.cython_function_or_method
delete_sec_context: _cython_3_2_4limitednofinalize.cython_function_or_method
export_sec_context: _cython_3_2_4limitednofinalize.cython_function_or_method
import_sec_context: _cython_3_2_4limitednofinalize.cython_function_or_method
init_sec_context: _cython_3_2_4limitednofinalize.cython_function_or_method
inquire_context: _cython_3_2_4limitednofinalize.cython_function_or_method
process_context_token: _cython_3_2_4limitednofinalize.cython_function_or_method

class SecurityContext:
    @classmethod
    def __init__(cls, *args, **kwargs) -> None: ...
    def __reduce__(self): ...
