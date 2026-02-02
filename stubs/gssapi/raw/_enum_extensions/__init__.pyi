import typing as t
from enum import EnumMeta

def register_value(cl_str: str, name: str, value: t.Any) -> None: ...

class ExtendableEnum(EnumMeta):
    def __new__(
        metacl, name: str, bases: tuple[type], classdict: dict[str, t.Any]
    ) -> ExtendableEnum: ...
