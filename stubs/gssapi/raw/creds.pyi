import _cython_3_2_4limitednofinalize
from gssapi.raw.misc import GSSError as GSSError
from gssapi.raw.named_tuples import AcquireCredResult as AcquireCredResult, AddCredResult as AddCredResult, InquireCredByMechResult as InquireCredByMechResult, InquireCredResult as InquireCredResult
from gssapi.raw.types import MechType as MechType, NameType as NameType

GSSAPI: str
__reduce_cython__: _cython_3_2_4limitednofinalize.cython_function_or_method
__setstate_cython__: _cython_3_2_4limitednofinalize.cython_function_or_method
__test__: dict
acquire_cred: _cython_3_2_4limitednofinalize.cython_function_or_method
add_cred: _cython_3_2_4limitednofinalize.cython_function_or_method
inquire_cred: _cython_3_2_4limitednofinalize.cython_function_or_method
inquire_cred_by_mech: _cython_3_2_4limitednofinalize.cython_function_or_method
release_cred: _cython_3_2_4limitednofinalize.cython_function_or_method

class Creds:
    @classmethod
    def __init__(cls, *args, **kwargs) -> None: ...
    def __reduce__(self): ...
