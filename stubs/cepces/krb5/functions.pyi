from _typeshed import Incomplete

class Error(RuntimeError):
    def __init__(self, context, code) -> None: ...
    @property
    def code(self): ...

def error_decorator(func): ...

krb5_cc_close: Incomplete
cc_close: Incomplete
krb5_cc_initialize: Incomplete
cc_initialize: Incomplete
krb5_cc_resolve: Incomplete
cc_resolve: Incomplete
krb5_cc_store_cred: Incomplete
cc_store_cred: Incomplete
krb5_free_context: Incomplete
free_context: Incomplete
krb5_free_cred_contents: Incomplete
free_cred_contents: Incomplete
krb5_free_error_message: Incomplete
free_error_message: Incomplete
krb5_free_principal: Incomplete
free_principal: Incomplete
krb5_free_unparsed_name: Incomplete
free_unparsed_name: Incomplete
krb5_get_error_message: Incomplete
get_error_message: Incomplete
krb5_get_init_creds_keytab: Incomplete
get_init_creds_keytab: Incomplete
krb5_get_init_creds_opt_alloc: Incomplete
get_init_creds_opt_alloc: Incomplete
krb5_get_init_creds_opt_free: Incomplete
get_init_creds_opt_free: Incomplete
krb5_get_init_creds_opt_set_etype_list: Incomplete
get_init_creds_opt_set_etype_list: Incomplete
krb5_get_init_creds_opt_set_forwardable: Incomplete
get_init_creds_opt_set_forwardable: Incomplete
krb5_init_context: Incomplete
init_context: Incomplete
krb5_kt_close: Incomplete
kt_close: Incomplete
krb5_kt_default: Incomplete
kt_default: Incomplete
krb5_kt_default_name: Incomplete
kt_default_name: Incomplete
krb5_kt_get_name: Incomplete
kt_get_name: Incomplete
krb5_kt_get_type: Incomplete
kt_get_type: Incomplete
krb5_kt_resolve: Incomplete
kt_resolve: Incomplete
krb5_parse_name: Incomplete
parse_name: Incomplete
krb5_sname_to_principal: Incomplete
sname_to_principal: Incomplete
krb5_unparse_name: Incomplete
unparse_name: Incomplete
