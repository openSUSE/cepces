from .gssapi_ import (
    DISABLED as DISABLED,
    HTTPSPNEGOAuth as HTTPSPNEGOAuth,
    SPNEGOExchangeError as SPNEGOExchangeError,
    log as log,
)
from _typeshed import Incomplete
from logging import NullHandler as NullHandler

class HTTPKerberosAuth(HTTPSPNEGOAuth):
    principal: Incomplete
    service: Incomplete
    hostname_override: Incomplete
    def __init__(
        self,
        mutual_authentication=...,
        service: str = "HTTP",
        delegate: bool = False,
        force_preemptive: bool = False,
        principal: Incomplete | None = None,
        hostname_override: Incomplete | None = None,
        sanitize_mutual_error_response: bool = True,
    ) -> None: ...
    creds: Incomplete
    target_name: Incomplete
    def generate_request_header(self, response, host, is_preemptive: bool = False): ...
