# Type stubs for cepces.wstep.types
#
# These stubs provide explicit type annotations for XML binding classes
# to fix reportUnknownMemberType warnings from the dynamic descriptor system.

from xml.etree.ElementTree import Element

from cepces.xml.binding import XMLNode

class Reference(XMLNode):
    """WS-Security Reference element for pointing to security tokens."""

    uri: str | None

    @staticmethod
    def create() -> None: ...

class SecurityTokenReference(XMLNode):
    """WS-Security SecurityTokenReference for referencing tokens."""

    reference: Reference | None

    @staticmethod
    def create() -> None: ...

class RequestedToken(XMLNode):
    """WS-Trust RequestedSecurityToken containing the issued certificate."""

    text: str | None
    token_reference: SecurityTokenReference | None

    @staticmethod
    def create() -> None: ...

class SecurityTokenRequest(XMLNode):
    """WS-Trust RequestSecurityToken (RST) message for certificate enrollment."""

    token_type: str | None
    request_type: str
    request_id: int
    token: str

    @staticmethod
    def create() -> Element: ...

class SecurityTokenResponse(XMLNode):
    """WS-Trust RequestSecurityTokenResponse (RSTR) from the server."""

    token_type: str | None
    disposition_message: str
    token: str
    requested_token: RequestedToken
    request_id: int

    @staticmethod
    def create() -> None: ...

class SecurityTokenResponseCollection(XMLNode):
    """WS-Trust RequestSecurityTokenResponseCollection (RSTRC)."""

    responses: list[SecurityTokenResponse] | None

    @staticmethod
    def create() -> None: ...
