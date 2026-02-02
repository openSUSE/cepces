from .exceptions import MutualAuthenticationError as MutualAuthenticationError, SPNEGOExchangeError as SPNEGOExchangeError
from _typeshed import Incomplete
from requests.auth import AuthBase
from requests.models import Response

log: Incomplete
REQUIRED: int
OPTIONAL: int
DISABLED: int
SPNEGO: Incomplete

class SanitizedResponse(Response):
    status_code: Incomplete
    encoding: Incomplete
    raw: Incomplete
    reason: Incomplete
    url: Incomplete
    request: Incomplete
    connection: Incomplete
    cookies: Incomplete
    headers: Incomplete
    def __init__(self, response) -> None: ...

class HTTPSPNEGOAuth(AuthBase):
    context: Incomplete
    pos: Incomplete
    mutual_authentication: Incomplete
    target_name: Incomplete
    delegate: Incomplete
    opportunistic_auth: Incomplete
    creds: Incomplete
    mech: Incomplete
    sanitize_mutual_error_response: Incomplete
    channel_bindings: Incomplete
    def __init__(self, mutual_authentication=..., target_name: str = 'HTTP', delegate: bool = False, opportunistic_auth: bool = False, creds=None, mech=..., sanitize_mutual_error_response: bool = True, channel_bindings=None) -> None: ...
    def generate_request_header(self, response, host, is_preemptive: bool = False): ...
    def authenticate_user(self, response, **kwargs): ...
    def handle_401(self, response, **kwargs): ...
    def handle_other(self, response): ...
    def authenticate_server(self, response): ...
    def handle_response(self, response, **kwargs): ...
    def deregister(self, response) -> None: ...
    def __call__(self, request): ...
