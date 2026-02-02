from gssapi.raw.exceptions import *
from _typeshed import Incomplete
from gssapi.raw.misc import GSSError as GSSError

class GeneralError(Exception):
    MAJOR_MESSAGE: str
    FMT_STR: str
    def __init__(self, minor_message: str, **kwargs: str) -> None: ...

class UnknownUsageError(GeneralError):
    MAJOR_MESSAGE: str

class EncryptionNotUsed(GeneralError):
    MAJOR_MESSAGE: str
    unwrapped_message: Incomplete
    def __init__(self, minor_message: str, unwrapped_message: bytes | None = None, **kwargs: str) -> None: ...
