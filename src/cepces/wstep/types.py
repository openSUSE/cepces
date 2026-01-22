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
"""WSTEP Types.

This module implements XML binding types for the WS-Trust (Web Services Trust
Language) protocol used for certificate enrollment via MS-WSTEP (Microsoft
Windows Server Certificate Enrollment Protocol).

The types defined here follow the OASIS WS-Security specifications:

- OASIS Web Services Security: SOAP Message Security 1.0
  https://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0.pdf

Key Namespaces:
- wst (WS-Trust): http://docs.oasis-open.org/ws-sx/ws-trust/200512
  Defines trust-related elements like RequestSecurityToken, TokenType, etc.

- wsse (WS-Security Extension): http://docs.oasis-open.org/wss/2004/01/
  oasis-200401-wss-wssecurity-secext-1.0.xsd
  Defines security token elements like BinarySecurityToken,
  SecurityTokenReference.

- wsu (WS-Security Utility): http://docs.oasis-open.org/wss/2004/01/
  oasis-200401-wss-wssecurity-utility-1.0.xsd
  Defines utility elements like Id attributes for element identification.

Key Elements (from WS-Security SOAP Message Security 1.0):
- BinarySecurityToken (Section 6.3): A security token that is binary encoded
  (e.g., X.509 certificates). Contains ValueType and EncodingType attributes.

- SecurityTokenReference (Section 7): A mechanism for referencing security
  tokens. Can contain Reference elements pointing to tokens by URI.

- Reference (Section 7.2): References a security token using a URI. The URI
  attribute identifies the referenced token.
"""

from xml.etree.ElementTree import Element, QName
from cepces.wstep import NS_WST, NS_WST_SECEXT, NS_WST_UTILITY, NS_ENROLLMENT
from cepces.wstep import TOKEN_TYPE, VALUE_TYPE, ENCODING_TYPE
from cepces.wstep import ISSUE_REQUEST_TYPE
from cepces.xml.binding import XMLAttribute
from cepces.xml.binding import XMLElement, XMLElementList
from cepces.xml.binding import XMLNode, XMLValue
from cepces.xml.converter import CertificateConverter
from cepces.xml.converter import StringConverter, UnsignedIntegerConverter


class SecurityTokenRequest(XMLNode):
    """WS-Trust RequestSecurityToken (RST) message for certificate enrollment.

    This class represents the wst:RequestSecurityToken element used to request
    a security token (certificate) from a Security Token Service (STS).

    See WS-Trust 1.3 specification for the RST structure.

    XML Structure::

        <wst:RequestSecurityToken>
            <wst:TokenType>...</wst:TokenType>
            <wst:RequestType>...</wst:RequestType>
            <wsse:BinarySecurityToken
                ValueType="..."
                EncodingType="..."
                wsu:Id="...">
                [Base64-encoded CSR]
            </wsse:BinarySecurityToken>
        </wst:RequestSecurityToken>

    Attributes:
        token_type: The type of token being requested
            (e.g., X.509v3 certificate). Maps to wst:TokenType element.
        request_type: The type of request operation
            (e.g., Issue, Renew, Cancel). Maps to wst:RequestType element.
        request_id: MS-WSTEP specific request identifier for tracking.
            Maps to enrollment:RequestID element.
        token: The Certificate Signing Request (CSR) as a BinarySecurityToken.
            Contains the base64-encoded PKCS#10 CSR.
            See WS-Security Section 6.3.
    """

    # wst:TokenType - Specifies the desired token type (optional per XSD)
    # <xs:element ref='wst:TokenType' minOccurs='0' />
    token_type = XMLValue(
        "TokenType",
        converter=StringConverter,
        namespace=NS_WST,
        required=False,
    )

    # wst:RequestType - Specifies the request action
    # (Issue, Renew, Cancel, etc.)
    request_type = XMLValue(
        "RequestType", converter=StringConverter, namespace=NS_WST
    )

    # enrollment:RequestID - MS-WSTEP specific identifier for request tracking
    request_id = XMLValue(
        "RequestID",
        converter=UnsignedIntegerConverter,
        namespace=NS_ENROLLMENT,
    )

    # wsse:BinarySecurityToken - Contains the base64-encoded CSR
    # See WS-Security Section 6.3 for BinarySecurityToken specification
    token = XMLValue(
        "BinarySecurityToken",
        converter=StringConverter,
        namespace=NS_WST_SECEXT,
    )

    @staticmethod
    def create():
        """Create a new RequestSecurityToken XML element.

        Constructs a wst:RequestSecurityToken element with the required child
        elements for submitting a certificate signing request via MS-WSTEP.

        Returns:
            Element: A new RequestSecurityToken XML element with TokenType,
                RequestType, and an empty BinarySecurityToken ready to be
                populated with a CSR.
        """
        # Create the root wst:RequestSecurityToken element
        element = Element(QName(NS_WST, "RequestSecurityToken"))  # type: ignore[type-var]  # noqa: E501

        # Add wst:TokenType specifying we want an X.509 certificate
        token_type = Element(QName(NS_WST, "TokenType"))  # type: ignore[type-var]  # noqa: E501
        token_type.text = TOKEN_TYPE
        element.append(token_type)

        # Add wst:RequestType specifying this is an Issue request
        request_type = Element(QName(NS_WST, "RequestType"))  # type: ignore[type-var]  # noqa: E501
        request_type.text = ISSUE_REQUEST_TYPE
        element.append(request_type)

        # Add wsse:BinarySecurityToken for the CSR
        token = Element(QName(NS_WST_SECEXT, "BinarySecurityToken"))  # type: ignore[type-var]  # noqa: E501

        # ValueType attribute (WS-Security Section 6.3):
        # Indicates the type of security token. For certificate enrollment,
        # this is a PKCS#10 Certificate Signing Request (CSR).
        token.set(QName("ValueType"), VALUE_TYPE)  # type: ignore[arg-type]  # noqa: E501

        # EncodingType attribute (WS-Security Section 6.3):
        # Specifies how the binary data is encoded. Uses Base64 encoding
        # as defined in the WS-Security specification.
        token.set(QName("EncodingType"), ENCODING_TYPE)  # type: ignore[arg-type] # noqa: E501

        # wsu:Id attribute (WS-Security Utility):
        # Unique identifier that allows this token to be referenced by
        # SecurityTokenReference elements elsewhere in the message.
        # Initially empty, set by caller before sending.
        token.set(QName(NS_WST_UTILITY, "Id"), "")  # type: ignore[arg-type]

        element.append(token)

        return element


class Reference(XMLNode):
    """WS-Security Reference element for pointing to security tokens.

    This class represents the wsse:Reference element as defined in
    WS-Security Section 7.2. It provides a mechanism to reference a
    security token using a URI.

    The Reference element is typically used within a SecurityTokenReference
    to point to a BinarySecurityToken or other security token element.

    XML Structure::

        <wsse:Reference URI="#token-id"/>

    Attributes:
        uri: The URI attribute that identifies the referenced security token.
            Typically a fragment identifier (e.g., "#token-id") pointing to
            the wsu:Id of the target token. See WS-Security Section 7.2.
    """

    # URI attribute - Fragment identifier pointing to the referenced token
    # See WS-Security Section 7.2 for Reference element specification
    uri = XMLAttribute("URI", converter=StringConverter)

    @staticmethod
    def create():
        """Create a new Reference XML element.

        Returns:
            None: Reference elements are typically created as part of
                SecurityTokenReference, not standalone.
        """
        return None


class SecurityTokenReference(XMLNode):
    """WS-Security SecurityTokenReference (STR) for referencing tokens.

    This class represents the wsse:SecurityTokenReference element as defined
    in WS-Security Section 7. It provides a standard mechanism for referencing
    security tokens that may be embedded in the message or located externally.

    The STR acts as an indirection mechanism, allowing security tokens to be
    referenced without embedding them directly in the referencing location.

    XML Structure::

        <wsse:SecurityTokenReference>
            <wsse:Reference URI="#token-id"/>
        </wsse:SecurityTokenReference>

    Attributes:
        reference: A Reference element containing a URI pointing to the
            security token. See WS-Security Section 7.2.
    """

    # wsse:Reference - Child element containing the URI to the referenced token
    # See WS-Security Section 7 for SecurityTokenReference specification
    reference = XMLElement(
        "Reference", binder=Reference, namespace=NS_WST_SECEXT, required=False
    )

    @staticmethod
    def create():
        """Create a new SecurityTokenReference XML element.

        Returns:
            None: SecurityTokenReference elements are created by the server
                in response messages, not by the client.
        """
        return None


class RequestedToken(XMLNode):
    """WS-Trust RequestedSecurityToken containing the issued certificate.

    This class represents the wst:RequestedSecurityToken element returned
    in a RequestSecurityTokenResponse. It contains the issued security token
    (certificate) along with optional references.

    The issued certificate is contained in a BinarySecurityToken element
    as defined in WS-Security Section 6.3.

    XML Structure::

        <wst:RequestedSecurityToken>
            <wsse:BinarySecurityToken
                ValueType="..."
                EncodingType="...">
                [Base64-encoded X.509 certificate]
            </wsse:BinarySecurityToken>
            <wsse:SecurityTokenReference>
                <wsse:Reference URI="#cert-id"/>
            </wsse:SecurityTokenReference>
        </wst:RequestedSecurityToken>

    Attributes:
        text: The issued X.509 certificate as a BinarySecurityToken.
            Contains the base64-encoded DER certificate.
            See WS-Security Section 6.3.
        token_reference: Optional SecurityTokenReference for referencing
            the issued token. See WS-Security Section 7.
    """

    # wsse:BinarySecurityToken - Contains the issued X.509 certificate
    # The CertificateConverter handles base64 decoding to X509 object
    # See WS-Security Section 6.3 for BinarySecurityToken specification
    text = XMLValue(
        "BinarySecurityToken",
        converter=CertificateConverter,
        namespace=NS_WST_SECEXT,
    )

    # wsse:SecurityTokenReference - Optional reference to the issued token
    # See WS-Security Section 7 for SecurityTokenReference specification
    token_reference = XMLElement(
        "SecurityTokenReference",
        binder=SecurityTokenReference,
        namespace=NS_WST_SECEXT,
        required=False,
    )

    @staticmethod
    def create():
        """Create a new RequestedSecurityToken XML element.

        Returns:
            None: RequestedSecurityToken elements are created by the server,
                not by the client.
        """
        return None


class SecurityTokenResponse(XMLNode):
    """WS-Trust RequestSecurityTokenResponse (RSTR) from the server.

    This class represents the wst:RequestSecurityTokenResponse element
    returned by the Security Token Service (STS) in response to a
    RequestSecurityToken request.

    The RSTR contains the issued certificate (if approved) along with
    status information and MS-WSTEP specific enrollment data.

    XML Structure::

        <wst:RequestSecurityTokenResponse>
            <wst:TokenType>...</wst:TokenType>
            <wst:RequestedSecurityToken>
                <wsse:BinarySecurityToken>...</wsse:BinarySecurityToken>
            </wst:RequestedSecurityToken>
            <enrollment:DispositionMessage>...</enrollment:DispositionMessage>
            <enrollment:RequestID>...</enrollment:RequestID>
        </wst:RequestSecurityTokenResponse>

    Attributes:
        token_type: The type of token issued (e.g., X.509v3 certificate).
            Maps to wst:TokenType element.
        disposition_message: MS-WSTEP specific status message indicating
            the result of the enrollment request (e.g., "Issued", "Pending").
        token: Raw BinarySecurityToken content as a string.
        requested_token: The RequestedSecurityToken containing the issued
            certificate and optional references.
        request_id: MS-WSTEP specific request identifier for tracking.
            Matches the RequestID from the original request.
    """

    # wst:TokenType - Specifies the issued token type (optional per XSD)
    # <xs:element ref='wst:TokenType' minOccurs='0' />
    token_type = XMLValue(
        "TokenType",
        converter=StringConverter,
        namespace=NS_WST,
        required=False,
    )

    # enrollment:DispositionMessage - MS-WSTEP enrollment status
    # Values include: "Issued", "Pending", "Denied", etc.
    disposition_message = XMLValue(
        "DispositionMessage",
        converter=StringConverter,
        namespace=NS_ENROLLMENT,
    )

    # wsse:BinarySecurityToken - Raw token content (if present at this level)
    token = XMLValue(
        "BinarySecurityToken",
        converter=StringConverter,
        namespace=NS_WST_SECEXT,
    )

    # wst:RequestedSecurityToken - Contains the issued certificate
    # This is where the actual X.509 certificate is returned
    requested_token = XMLElement(
        "RequestedSecurityToken", binder=RequestedToken, namespace=NS_WST
    )

    # enrollment:RequestID - MS-WSTEP specific identifier for request tracking
    # Used to correlate responses with requests and for pending request polling
    request_id = XMLValue(
        "RequestID",
        converter=UnsignedIntegerConverter,
        namespace=NS_ENROLLMENT,
    )

    @staticmethod
    def create():
        """Create a new RequestSecurityTokenResponse XML element.

        Returns:
            None: RSTR elements are created by the server, not by the client.
        """
        return None


class SecurityTokenResponseCollection(XMLNode):
    """WS-Trust RequestSecurityTokenResponseCollection (RSTRC).

    This class represents the wst:RequestSecurityTokenResponseCollection
    element, which is a container for multiple RequestSecurityTokenResponse
    elements.

    This is used when a single request results in multiple responses,
    such as when requesting multiple certificates or when the server
    returns additional context tokens.

    XML Structure::

        <wst:RequestSecurityTokenResponseCollection>
            <wst:RequestSecurityTokenResponse>...</wst:RequestSecurityTokenResponse>
            <wst:RequestSecurityTokenResponse>...</wst:RequestSecurityTokenResponse>
            ...
        </wst:RequestSecurityTokenResponseCollection>

    Attributes:
        responses: A list of SecurityTokenResponse elements, each containing
            an individual response from the STS.
    """

    # List of wst:RequestSecurityTokenResponse elements
    # The "." path means children are direct descendants of this element
    responses = XMLElementList(
        ".",
        child_name="RequestSecurityTokenResponse",
        binder=SecurityTokenResponse,
        child_namespace=NS_WST,
    )

    @staticmethod
    def create():
        """Create a new RequestSecurityTokenResponseCollection XML element.

        Returns:
            None: RSTRC elements are created by the server, not by the client.
        """
        return None
