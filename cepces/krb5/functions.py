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
from cepces.krb5 import types as ktypes
from cepces.krb5.lib import _shlib
import ctypes
import functools


class Error(RuntimeError):
    def __init__(self, context, code):
        message_p = get_error_message(context, code)

        self._code = code
        self._message = message_p.value.decode('utf-8')
        super().__init__(self._message)

        free_error_message(context, message_p)

    @property
    def code(self):
        return self._code

    def __str__(self):
        return self._message


def error_decorator(f):
    if f.restype is not ktypes.krb5_error_code:
        return f

    @functools.wraps(f)
    def wrapper(context, *args):
        result = f(context, *args)

        # If the function call failed, raise an error.
        if result:
            raise Error(context, result)

        return result

    return wrapper


# krb5_error_code krb5_cc_close(krb5_context context, krb5_ccache cache)
krb5_cc_close = _shlib.krb5_cc_close
krb5_cc_close.restype = ktypes.krb5_error_code
krb5_cc_close.argtypes = [
    ktypes.krb5_context,
    ktypes.krb5_ccache,
]
cc_close = error_decorator(krb5_cc_close)

# krb5_error_code krb5_cc_initialize(krb5_context context, krb5_ccache cache,
#     krb5_principal principal)
krb5_cc_initialize = _shlib.krb5_cc_initialize
krb5_cc_initialize.restype = ktypes.krb5_error_code
krb5_cc_initialize.argtypes = [
    ktypes.krb5_context,
    ktypes.krb5_ccache,
    ktypes.krb5_principal,
]
cc_initialize = error_decorator(krb5_cc_initialize)

# krb5_error_code krb5_cc_resolve(krb5_context context, const char * name,
#     krb5_ccache * cache)
krb5_cc_resolve = _shlib.krb5_cc_resolve
krb5_cc_resolve.restype = ktypes.krb5_error_code
krb5_cc_resolve.argtypes = [
    ktypes.krb5_context,
    ctypes.c_char_p,
    ctypes.POINTER(ktypes.krb5_ccache),
]
cc_resolve = error_decorator(krb5_cc_resolve)

# krb5_error_code krb5_cc_store_cred(krb5_context context, krb5_ccache cache,
#     krb5_creds * creds)
krb5_cc_store_cred = _shlib.krb5_cc_store_cred
krb5_cc_store_cred.restype = ktypes.krb5_error_code
krb5_cc_store_cred.argtypes = [
    ktypes.krb5_context,
    ktypes.krb5_ccache,
    ctypes.POINTER(ktypes.krb5_creds),
]
cc_store_cred = error_decorator(krb5_cc_store_cred)


# void krb5_free_context(krb5_context context)
krb5_free_context = _shlib.krb5_free_context
krb5_free_context.restype = None
krb5_free_context.argtypes = [
    ktypes.krb5_context,
]
free_context = error_decorator(krb5_free_context)

# void krb5_free_cred_contents(krb5_context context, krb5_creds * val)
krb5_free_cred_contents = _shlib.krb5_free_cred_contents
krb5_free_cred_contents.restype = None
krb5_free_cred_contents.argtypes = [
    ktypes.krb5_context,
    ctypes.POINTER(ktypes.krb5_creds),
]
free_cred_contents = error_decorator(krb5_free_cred_contents)


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

# krb5_error_code krb5_get_init_creds_keytab(krb5_context context,
#     krb5_creds * creds, krb5_principal client, krb5_keytab arg_keytab,
#     krb5_deltat start_time, const char * in_tkt_service,
#     krb5_get_init_creds_opt * k5_gic_options)
krb5_get_init_creds_keytab = _shlib.krb5_get_init_creds_keytab
krb5_get_init_creds_keytab.restype = ktypes.krb5_error_code
krb5_get_init_creds_keytab.argtypes = [
    ktypes.krb5_context,
    ctypes.POINTER(ktypes.krb5_creds),
    ktypes.krb5_principal,
    ktypes.krb5_keytab,
    ktypes.krb5_deltat,
    ctypes.c_char_p,
    ctypes.POINTER(ktypes.krb5_get_init_creds_opt),
]
get_init_creds_keytab = error_decorator(krb5_get_init_creds_keytab)

# krb5_error_code krb5_get_init_creds_opt_alloc(krb5_context context,
#     krb5_get_init_creds_opt ** opt)
krb5_get_init_creds_opt_alloc = _shlib.krb5_get_init_creds_opt_alloc
krb5_get_init_creds_opt_alloc.restype = ktypes.krb5_error_code
krb5_get_init_creds_opt_alloc.argtypes = [
    ktypes.krb5_context,
    ctypes.POINTER(ctypes.POINTER(ktypes.krb5_get_init_creds_opt)),
]
get_init_creds_opt_alloc = error_decorator(krb5_get_init_creds_opt_alloc)

# void krb5_get_init_creds_opt_free(krb5_context context,
#     krb5_get_init_creds_opt * opt)
krb5_get_init_creds_opt_free = _shlib.krb5_get_init_creds_opt_free
krb5_get_init_creds_opt_free.restype = None
krb5_get_init_creds_opt_free.argtypes = [
    ktypes.krb5_context,
    ctypes.POINTER(ktypes.krb5_get_init_creds_opt),
]
get_init_creds_opt_free = error_decorator(krb5_get_init_creds_opt_free)

# void krb5_get_init_creds_opt_set_etype_list(krb5_get_init_creds_opt * opt,
#     krb5_enctype * etype_list, int etype_list_length)
krb5_get_init_creds_opt_set_etype_list = \
    _shlib.krb5_get_init_creds_opt_set_etype_list
krb5_get_init_creds_opt_set_etype_list.restype = None
krb5_get_init_creds_opt_set_etype_list.argtypes = [
    ctypes.POINTER(ktypes.krb5_get_init_creds_opt),
    ctypes.POINTER(ktypes.krb5_enctype),
    ctypes.c_int,
]
get_init_creds_opt_set_etype_list = \
    error_decorator(krb5_get_init_creds_opt_set_etype_list)

# void krb5_get_init_creds_opt_set_forwardable(krb5_get_init_creds_opt * opt,
#     int forwardable)
krb5_get_init_creds_opt_set_forwardable = \
    _shlib.krb5_get_init_creds_opt_set_forwardable
krb5_get_init_creds_opt_set_forwardable.restype = None
krb5_get_init_creds_opt_set_forwardable.argtypes = [
    ctypes.POINTER(ktypes.krb5_get_init_creds_opt),
    ctypes.c_int,
]
get_init_creds_opt_set_forwardable = \
    error_decorator(krb5_get_init_creds_opt_set_forwardable)

# krb5_error_code krb5_init_context(krb5_context * context)
krb5_init_context = _shlib.krb5_init_context
krb5_init_context.restype = ktypes.krb5_error_code
krb5_init_context.argtypes = [
    ctypes.POINTER(ktypes.krb5_context),
]
init_context = error_decorator(krb5_init_context)

# krb5_error_code krb5_kt_close(krb5_context context, krb5_keytab keytab)
krb5_kt_close = _shlib.krb5_kt_close
krb5_kt_close.restype = ktypes.krb5_error_code
krb5_kt_close.argtypes = [
    ktypes.krb5_context,
    ktypes.krb5_keytab,
]
kt_close = error_decorator(krb5_kt_close)

# krb5_error_code krb5_kt_default(krb5_context context, krb5_keytab * id)
krb5_kt_default = _shlib.krb5_kt_default
krb5_kt_default.restype = ktypes.krb5_error_code
krb5_kt_default.argtypes = [
    ktypes.krb5_context,
    ctypes.POINTER(ktypes.krb5_keytab),
]
kt_default = error_decorator(krb5_kt_default)

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

# krb5_error_code krb5_kt_get_name(krb5_context context, krb5_keytab keytab,
#     char * name, unsigned int namelen)
krb5_kt_get_name = _shlib.krb5_kt_get_name
krb5_kt_get_name.restype = ktypes.krb5_error_code
krb5_kt_get_name.argtypes = [
    ktypes.krb5_context,
    ktypes.krb5_keytab,
    ctypes.POINTER(ctypes.c_char),
    ctypes.c_uint,
]
kt_get_name = error_decorator(krb5_kt_get_name)

# const char * krb5_kt_get_type(krb5_context context, krb5_keytab keytab)
krb5_kt_get_type = _shlib.krb5_kt_get_type
krb5_kt_get_type.restype = ctypes.c_char_p
krb5_kt_get_type.argtypes = [
    ktypes.krb5_context,
    ktypes.krb5_keytab,
]
kt_get_type = error_decorator(krb5_kt_get_type)

# krb5_error_code krb5_kt_resolve(krb5_context context, const char * name,
#     krb5_keytab * ktid)
krb5_kt_resolve = _shlib.krb5_kt_resolve
krb5_kt_resolve.restype = ktypes.krb5_error_code
krb5_kt_resolve.argtypes = [
    ktypes.krb5_context,
    ctypes.c_char_p,
    ctypes.POINTER(ktypes.krb5_keytab),
]
kt_resolve = error_decorator(krb5_kt_resolve)

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
