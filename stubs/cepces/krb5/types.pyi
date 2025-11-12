import ctypes
from _typeshed import Incomplete
from enum import IntEnum

LINE_MAX: int
KRB5_TGS_NAME: str
krb5_int32 = ctypes.c_int32
krb5_enctype = krb5_int32
krb5_deltat = krb5_int32
krb5_error_code = krb5_int32

class PrincipalType(IntEnum):
    KRB5_NT_UNKNOWN = 0
    KRB5_NT_PRINCIPAL = 1
    KRB5_NT_SRV_INST = 2
    KRB5_NT_SRV_HST = 3
    KRB5_NT_SRV_XHST = 4
    KRB5_NT_UID = 5
    KRB5_NT_X500_PRINCIPAL = 6
    KRB5_NT_SMTP_NAME = 7
    KRB5_NT_ENTERPRISE_PRINCIPAL = 10
    KRB5_NT_WELLKNOWN = 11
    KRB5_NT_SRV_HST_DOMAIN = 12
    KRB5_NT_MS_PRINCIPAL = -128
    KRB5_NT_MS_PRINCIPAL_AND_ID = -129
    KRB5_NT_ENT_PRINCIPAL_AND_ID = -130
    KRB5_NT_NTLM = -1200
    KRB5_NT_X509_GENERAL_NAME = -1201
    KRB5_NT_CACHE_UUID = -1203

class EncryptionType(IntEnum):
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

class c_char_p_n(ctypes.c_char_p): ...
class _krb5_context(ctypes.Structure): ...

krb5_context: Incomplete

class _krb5_kt(ctypes.Structure): ...

krb5_keytab: Incomplete

class krb5_principal_data(ctypes.Structure): ...

krb5_principal: Incomplete
krb5_const_principal: Incomplete

class _krb5_get_init_creds_opt(ctypes.Structure): ...

krb5_get_init_creds_opt: Incomplete
krb5_get_init_creds_opt_p: Incomplete

class _krb5_creds(ctypes.Structure): ...

krb5_creds: Incomplete

class _krb5_ccache(ctypes.Structure): ...

krb5_ccache: Incomplete
