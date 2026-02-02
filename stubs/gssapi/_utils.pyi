import decorator as deco
import types
import typing as t
from gssapi.raw.misc import GSSError as GSSError
from gssapi.sec_contexts import SecurityContext as SecurityContext

def import_gssapi_extension(name: str) -> types.ModuleType | None: ...
def inquire_property(name: str, doc: str | None = None) -> property: ...
def set_encoding(enc: str) -> None: ...
@deco.decorator
def catch_and_return_token(
    func: t.Callable, self: SecurityContext, *args: t.Any, **kwargs: t.Any
) -> bytes | None: ...
@deco.decorator
def check_last_err(
    func: t.Callable, self: SecurityContext, *args: t.Any, **kwargs: t.Any
) -> t.Any: ...

class CheckLastError(type):
    def __new__(
        cls, name: str, parents: tuple[type], attrs: dict[str, t.Any]
    ) -> CheckLastError: ...
