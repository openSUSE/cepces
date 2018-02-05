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
# pylint: disable=invalid-name,too-few-public-methods
"""This module contains all Kerberos specific types and structures."""
import ctypes
from enum import IntEnum

LINE_MAX = 2048

# The name of the Kerberos ticket granting service
KRB5_TGS_NAME = 'krbtgt'

krb5_int32 = ctypes.c_int32
krb5_enctype = krb5_int32
krb5_deltat = krb5_int32
krb5_error_code = krb5_int32


class PrincipalType(IntEnum):
    """Enumeration for all possible principal types."""
    # Name type not known
    KRB5_NT_UNKNOWN = 0
    # Just the name of the principal as in DCE, or for users
    KRB5_NT_PRINCIPAL = 1
    # Service and other unique instance (krbtgt)
    KRB5_NT_SRV_INST = 2
    # Service with host name as instance (telnet, rcommands)
    KRB5_NT_SRV_HST = 3
    # Service with host as remaining components
    KRB5_NT_SRV_XHST = 4
    # Unique ID
    KRB5_NT_UID = 5
    # PKINIT
    KRB5_NT_X500_PRINCIPAL = 6
    # Name in form of SMTP email name
    KRB5_NT_SMTP_NAME = 7
    # Windows 2000 UPN
    KRB5_NT_ENTERPRISE_PRINCIPAL = 10
    # Well-known (special) principal
    KRB5_NT_WELLKNOWN = 11
    # Domain based service with host name as instance (RFC5179)
    KRB5_NT_SRV_HST_DOMAIN = 12
    # Windows 2000 UPN and SID
    KRB5_NT_MS_PRINCIPAL = -128
    # NT 4 style name
    KRB5_NT_MS_PRINCIPAL_AND_ID = -129
    # NT 4 style name and SID
    KRB5_NT_ENT_PRINCIPAL_AND_ID = -130
    # NTLM name, realm is domain
    KRB5_NT_NTLM = -1200
    # x509 general name (base64 encoded)
    KRB5_NT_X509_GENERAL_NAME = -1201
    # name is actually a uuid pointing to ccache, use client name in cache
    KRB5_NT_CACHE_UUID = -1203


class EncryptionType(IntEnum):
    """Enumeration for all possible encryption types."""
    KRB5_ENCTYPE_NULL = 0
    KRB5_ENCTYPE_DES_CBC_CRC = 1
    KRB5_ENCTYPE_DES_CBC_MD4 = 2
    KRB5_ENCTYPE_DES_CBC_MD5 = 3
    KRB5_ENCTYPE_DES_CBC_RAW = 4
    KRB5_ENCTYPE_DES3_CBC_SHA = 5
    KRB5_ENCTYPE_DES3_CBC_RAW = 6
    KRB5_ENCTYPE_OLD_DES3_CBC_SHA1 = 7
    KRB5_ENCTYPE_DES_HMAC_SHA1 = 8
    KRB5_ENCTYPE_DSA_SHA1_CMS = 9
    KRB5_ENCTYPE_MD5_RSA_CMS = 10
    KRB5_ENCTYPE_SHA1_RSA_CMS = 11
    KRB5_ENCTYPE_RC2_CBC_ENV = 12
    KRB5_ENCTYPE_RSA_ENV = 13
    KRB5_ENCTYPE_RSA_ES_OAEP_ENV = 14
    KRB5_ENCTYPE_DES3_CBC_ENV = 15
    KRB5_ENCTYPE_DES3_CBC_SHA1 = 16
    KRB5_ENCTYPE_AES128_CTS_HMAC_SHA1_96 = 17
    KRB5_ENCTYPE_AES256_CTS_HMAC_SHA1_96 = 18
    KRB5_ENCTYPE_AES128_CTS_HMAC_SHA256_128 = 19
    KRB5_ENCTYPE_AES256_CTS_HMAC_SHA384_192 = 20
    KRB5_ENCTYPE_ARCFOUR_HMAC = 23
    KRB5_ENCTYPE_ARCFOUR_HMAC_EXP = 24
    KRB5_ENCTYPE_CAMELLIA128_CTS_CMAC = 25
    KRB5_ENCTYPE_CAMELLIA256_CTS_CMAC = 26
    KRB5_ENCTYPE_UNKNOWN = 511


# ctypes converts c_char_p and then throws away the pointer. This child class
# prevents that behaviour.
class c_char_p_n(ctypes.c_char_p):
    """Opaque class for a character pointer."""
    pass


class _krb5_context(ctypes.Structure):
    """Opaque structure for a Kerberos context."""
    pass


krb5_context = ctypes.POINTER(_krb5_context)


class _krb5_kt(ctypes.Structure):
    """Opaque structure for a Kerberos keytab."""
    pass


krb5_keytab = ctypes.POINTER(_krb5_kt)


class krb5_principal_data(ctypes.Structure):
    """Opaque structure for a Kerberos principal data."""
    pass


krb5_principal = ctypes.POINTER(krb5_principal_data)
krb5_const_principal = ctypes.POINTER(krb5_principal_data)


class _krb5_get_init_creds_opt(ctypes.Structure):
    """Structure for Kerberos credential options."""
    _fields_ = [
        ('flags', krb5_int32),
        ('tkt_life', krb5_deltat),
        ('renew_life', krb5_deltat),
        ('forwardable', ctypes.c_int),
        ('proxiable', ctypes.c_int),
        ('etype_list', ctypes.POINTER(krb5_enctype)),
        ('etype_list_length', ctypes.c_int),
        ('address_list', ctypes.POINTER(ctypes.c_void_p)),
        ('preauth_list', ctypes.POINTER(krb5_int32)),
        ('preauth_list_length', ctypes.c_int),
        ('salt', ctypes.c_void_p),
    ]


krb5_get_init_creds_opt = _krb5_get_init_creds_opt
krb5_get_init_creds_opt_p = ctypes.POINTER(krb5_get_init_creds_opt)


class _krb5_creds(ctypes.Structure):
    """An opaque structure representing _krb5_creds.

    Since different Kerberos implementations have different structures,
    generate a "large enough" struct that can be filled by the Kerberos
    library.
    """
    _fields_ = [
        ('data', ctypes.c_byte * 256),
    ]


krb5_creds = _krb5_creds


class _krb5_ccache(ctypes.Structure):
    """Opaque structure for a Kerberos credential cache."""
    pass


krb5_ccache = ctypes.POINTER(_krb5_ccache)
