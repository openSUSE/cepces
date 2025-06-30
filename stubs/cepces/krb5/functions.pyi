from _typeshed import Incomplete

class Error(RuntimeError):
    def __init__(self, context, code) -> None: ...
    @property
    def code(self): ...

def error_decorator(func): ...

krb5_free_context: Incomplete
free_context: Incomplete
krb5_free_error_message: Incomplete
free_error_message: Incomplete
krb5_free_principal: Incomplete
free_principal: Incomplete
krb5_free_unparsed_name: Incomplete
free_unparsed_name: Incomplete
krb5_get_error_message: Incomplete
get_error_message: Incomplete
krb5_init_context: Incomplete
init_context: Incomplete
krb5_parse_name: Incomplete
parse_name: Incomplete
krb5_sname_to_principal: Incomplete
sname_to_principal: Incomplete
krb5_unparse_name: Incomplete
unparse_name: Incomplete
