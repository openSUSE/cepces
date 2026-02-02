import ctypes

__all__ = ['_shlib']

_shlib: ctypes.CDLL | None
