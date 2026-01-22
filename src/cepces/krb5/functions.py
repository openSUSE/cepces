# -*- coding: utf-8 -*-
#
# This file is part of cepces.
#
# cepces is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# cepces is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with cepces.  If not, see <http://www.gnu.org/licenses/>.
#
# pylint: disable=invalid-name
"""This module contains all the Kerberos functions."""

import ctypes
import functools
from cepces.krb5 import types as ktypes
from cepces.krb5.lib import _shlib

assert _shlib is not None  # Guaranteed by RuntimeError in lib.py


class Error(RuntimeError):
    """Generic error class, representing a runtime error from Kerberos."""

    def __init__(self, context, code):
        message_p = get_error_message(context, code)

        self._code = code
        self._message = message_p.value.decode("utf-8")
        super().__init__(self._message)

        free_error_message(context, message_p)

    @property
    def code(self):
        """Get the error code."""
        return self._code

    def __str__(self):
        return self._message


def error_decorator(func):
    """Decorator for wrapping a function that raises errors on failed
    Kerberos calls."""
    if func.restype is not ktypes.krb5_error_code:
        return func

    @functools.wraps(func)
    def wrapper(context, *args):
        """Wrapper function."""
        result = func(context, *args)

        # If the function call failed, raise an error.
        if result:
            raise Error(context, result)

        return result

    return wrapper


# void krb5_free_context(krb5_context context)
krb5_free_context = _shlib.krb5_free_context
krb5_free_context.restype = None
krb5_free_context.argtypes = [
    ktypes.krb5_context,
]
free_context = error_decorator(krb5_free_context)

# void krb5_free_error_message(krb5_context ctx, const char * msg)
krb5_free_error_message = _shlib.krb5_free_error_message
krb5_free_error_message.restype = None
krb5_free_error_message.argtypes = [
    ktypes.krb5_context,
    ktypes.c_char_p_n,
]
free_error_message = error_decorator(krb5_free_error_message)

# void krb5_free_principal(krb5_context context, krb5_principal val)
krb5_free_principal = _shlib.krb5_free_principal
krb5_free_principal.restype = None
krb5_free_principal.argtypes = [
    ktypes.krb5_context,
    ktypes.krb5_principal,
]
free_principal = error_decorator(krb5_free_principal)

# void krb5_free_unparsed_name(krb5_context context, char * val)
krb5_free_unparsed_name = _shlib.krb5_free_unparsed_name
krb5_free_unparsed_name.restype = None
krb5_free_unparsed_name.argtypes = [
    ktypes.krb5_context,
    ctypes.c_char_p,
]
free_unparsed_name = error_decorator(krb5_free_unparsed_name)

# const char * krb5_get_error_message(krb5_context ctx, krb5_error_code code)
krb5_get_error_message = _shlib.krb5_get_error_message
krb5_get_error_message.restype = ktypes.c_char_p_n
krb5_get_error_message.argtypes = [
    ktypes.krb5_context,
    ktypes.krb5_error_code,
]
get_error_message = error_decorator(krb5_get_error_message)

# krb5_error_code krb5_init_context(krb5_context * context)
krb5_init_context = _shlib.krb5_init_context
krb5_init_context.restype = ktypes.krb5_error_code
krb5_init_context.argtypes = [
    ctypes.POINTER(ktypes.krb5_context),
]
init_context = error_decorator(krb5_init_context)

# krb5_error_code krb5_kt_default_name(krb5_context context, char * name,
#     int name_size)
krb5_kt_default_name = _shlib.krb5_kt_default_name
krb5_kt_default_name.restype = ktypes.krb5_error_code
krb5_kt_default_name.argtypes = [
    ktypes.krb5_context,
    ctypes.POINTER(ctypes.c_char),
    ctypes.c_uint,
]
kt_default_name = error_decorator(krb5_kt_default_name)

# krb5_error_code krb5_kt_default(krb5_context context, krb5_keytab * id)
krb5_parse_name = _shlib.krb5_parse_name
krb5_parse_name.restype = ktypes.krb5_error_code
krb5_parse_name.argtypes = [
    ktypes.krb5_context,
    ctypes.c_char_p,
    ctypes.POINTER(ktypes.krb5_principal),
]
parse_name = error_decorator(krb5_parse_name)

# krb5_error_code krb5_sname_to_principal(krb5_context context,
#     const char * hostname, const char * sname, krb5_int32 type,
#     krb5_principal * ret_princ)
krb5_sname_to_principal = _shlib.krb5_sname_to_principal
krb5_sname_to_principal.restype = ktypes.krb5_error_code
krb5_sname_to_principal.argtypes = [
    ktypes.krb5_context,
    ctypes.c_char_p,
    ctypes.c_char_p,
    ktypes.krb5_int32,
    ctypes.POINTER(ktypes.krb5_principal),
]
sname_to_principal = error_decorator(krb5_sname_to_principal)

# krb5_error_code krb5_unparse_name(krb5_context context,
#     krb5_const_principal principal, register char ** name)
krb5_unparse_name = _shlib.krb5_unparse_name
krb5_unparse_name.restype = ktypes.krb5_error_code
krb5_unparse_name.argtypes = [
    ktypes.krb5_context,
    ktypes.krb5_const_principal,
    ctypes.POINTER(ctypes.c_char_p),
]
unparse_name = error_decorator(krb5_unparse_name)
