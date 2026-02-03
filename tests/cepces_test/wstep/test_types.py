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
from xml.etree import ElementTree

from cepces.wstep.types import SecurityTokenRequest
from cepces.wstep.types import Reference
from cepces.wstep.types import SecurityTokenReference
from cepces.wstep.types import RequestedToken
from cepces.wstep.types import SecurityTokenResponse
from cepces.wstep.types import SecurityTokenResponseCollection
from cepces.wstep import NS_WST, NS_WST_SECEXT, NS_WST_UTILITY, NS_ENROLLMENT
from cepces.wstep import (
    TOKEN_TYPE,
    VALUE_TYPE,
    ENCODING_TYPE,
    ISSUE_REQUEST_TYPE,
)


class TestSecurityTokenRequestCreate:
    """Tests for SecurityTokenRequest.create() method."""

    def test_creates_request_security_token_element(self):
        """create() should return a RequestSecurityToken element."""
        element = SecurityTokenRequest.create()

        assert element.tag == f"{{{NS_WST}}}RequestSecurityToken"

    def test_has_token_type_element(self):
        """RequestSecurityToken should contain TokenType element."""
        element = SecurityTokenRequest.create()

        token_type = element.find(f"{{{NS_WST}}}TokenType")
        assert token_type is not None, "TokenType element not found"
        assert token_type.text == TOKEN_TYPE

    def test_has_request_type_element(self):
        """RequestSecurityToken should contain RequestType element."""
        element = SecurityTokenRequest.create()

        request_type = element.find(f"{{{NS_WST}}}RequestType")
        assert request_type is not None, "RequestType element not found"
        assert request_type.text == ISSUE_REQUEST_TYPE

    def test_has_binary_security_token_element(self):
        """RequestSecurityToken should contain BinarySecurityToken element."""
        element = SecurityTokenRequest.create()

        token = element.find(f"{{{NS_WST_SECEXT}}}BinarySecurityToken")
        assert token is not None, "BinarySecurityToken element not found"

    def test_binary_security_token_has_value_type(self):
        """BinarySecurityToken must have ValueType attribute."""
        element = SecurityTokenRequest.create()

        token = element.find(f"{{{NS_WST_SECEXT}}}BinarySecurityToken")
        assert token is not None

        value_type = token.get("ValueType")
        assert value_type is not None, "ValueType attribute is missing"
        assert value_type == VALUE_TYPE

    def test_binary_security_token_has_encoding_type(self):
        """BinarySecurityToken must have EncodingType attribute.

        When requesting a certificate, IIS returns HTTP 500 with error:
        "The EncodingType is invalid." if the BinarySecurityToken element
        does not have the EncodingType attribute set.

        The EncodingType attribute is required by WS-Security spec and must be:
        http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd#base64binary
        """
        element = SecurityTokenRequest.create()

        token = element.find(f"{{{NS_WST_SECEXT}}}BinarySecurityToken")
        assert token is not None

        encoding_type = token.get("EncodingType")
        assert encoding_type is not None, "EncodingType attribute is missing"
        assert (
            encoding_type == ENCODING_TYPE
        ), f"EncodingType should be {ENCODING_TYPE}, got {encoding_type}"

    def test_binary_security_token_has_wsu_id(self):
        """BinarySecurityToken must have wsu:Id attribute."""
        element = SecurityTokenRequest.create()

        token = element.find(f"{{{NS_WST_SECEXT}}}BinarySecurityToken")
        assert token is not None

        wsu_id = token.get(f"{{{NS_WST_UTILITY}}}Id")
        assert wsu_id is not None, "wsu:Id attribute is missing"


class TestReference:
    """Tests for Reference XMLNode."""

    def test_create_returns_none(self):
        """Reference.create() should return None."""
        assert Reference.create() is None

    def test_uri_attribute_parsing(self):
        """Reference should parse URI attribute."""
        xml = f'<Reference xmlns="{NS_WST_SECEXT}" ' f'URI="#token123" />'
        element = ElementTree.fromstring(xml)
        ref = Reference(element)

        assert ref.uri == "#token123"


class TestSecurityTokenReference:
    """Tests for SecurityTokenReference XMLNode."""

    def test_create_returns_none(self):
        """SecurityTokenReference.create() should return None."""
        assert SecurityTokenReference.create() is None

    def test_reference_element_parsing(self):
        """SecurityTokenReference should parse Reference child element."""
        xml = f"""
        <SecurityTokenReference xmlns="{NS_WST_SECEXT}">
            <Reference URI="#token456" />
        </SecurityTokenReference>
        """
        element = ElementTree.fromstring(xml)
        str_node = SecurityTokenReference(element)

        assert str_node.reference is not None
        assert str_node.reference.uri == "#token456"

    def test_reference_element_optional(self):
        """SecurityTokenReference Reference element is optional."""
        xml = f'<SecurityTokenReference xmlns="{NS_WST_SECEXT}" />'
        element = ElementTree.fromstring(xml)
        str_node = SecurityTokenReference(element)

        assert str_node.reference is None


class TestRequestedToken:
    """Tests for RequestedToken XMLNode."""

    def test_create_returns_none(self):
        """RequestedToken.create() should return None."""
        assert RequestedToken.create() is None


class TestSecurityTokenResponse:
    """Tests for SecurityTokenResponse XMLNode."""

    def test_create_returns_none(self):
        """SecurityTokenResponse.create() should return None."""
        assert SecurityTokenResponse.create() is None

    def test_disposition_message_parsing(self):
        """SecurityTokenResponse should parse DispositionMessage."""
        xml = f"""<RequestSecurityTokenResponse xmlns="{NS_WST}">
        <DispositionMessage xmlns="{NS_ENROLLMENT}">Issued</DispositionMessage>
        <RequestID xmlns="{NS_ENROLLMENT}">12345</RequestID>
        </RequestSecurityTokenResponse>"""
        element = ElementTree.fromstring(xml)
        response = SecurityTokenResponse(element)

        assert response.disposition_message == "Issued"

    def test_request_id_parsing(self):
        """SecurityTokenResponse should parse RequestID as unsigned integer."""
        xml = f"""<RequestSecurityTokenResponse xmlns="{NS_WST}">
        <DispositionMessage xmlns="{NS_ENROLLMENT}">Issued</DispositionMessage>
        <RequestID xmlns="{NS_ENROLLMENT}">12345</RequestID>
        </RequestSecurityTokenResponse>"""
        element = ElementTree.fromstring(xml)
        response = SecurityTokenResponse(element)

        assert response.request_id == 12345

    def test_token_type_optional(self):
        """SecurityTokenResponse TokenType element is optional."""
        xml = f"""<RequestSecurityTokenResponse xmlns="{NS_WST}">
        <DispositionMessage xmlns="{NS_ENROLLMENT}">Issued</DispositionMessage>
        <RequestID xmlns="{NS_ENROLLMENT}">12345</RequestID>
        </RequestSecurityTokenResponse>"""
        element = ElementTree.fromstring(xml)
        response = SecurityTokenResponse(element)

        assert response.token_type is None


class TestSecurityTokenResponseCollection:
    """Tests for SecurityTokenResponseCollection XMLNode."""

    def test_create_returns_none(self):
        """SecurityTokenResponseCollection.create() should return None."""
        assert SecurityTokenResponseCollection.create() is None

    def test_responses_list_parsing(self):
        """SecurityTokenResponseCollection should parse list of responses."""
        xml = f"""<RequestSecurityTokenResponseCollection xmlns="{NS_WST}">
        <RequestSecurityTokenResponse>
        <DispositionMessage xmlns="{NS_ENROLLMENT}">Issued</DispositionMessage>
        <RequestID xmlns="{NS_ENROLLMENT}">1</RequestID>
        </RequestSecurityTokenResponse>
        <RequestSecurityTokenResponse>
        <DispositionMessage xmlns="{NS_ENROLLMENT}">Wait</DispositionMessage>
        <RequestID xmlns="{NS_ENROLLMENT}">2</RequestID>
        </RequestSecurityTokenResponse>
        </RequestSecurityTokenResponseCollection>"""
        element = ElementTree.fromstring(xml)
        collection = SecurityTokenResponseCollection(element)

        assert collection.responses is not None
        assert len(collection.responses) == 2
        assert collection.responses[0].disposition_message == "Issued"
        assert collection.responses[0].request_id == 1
        assert collection.responses[1].disposition_message == "Wait"
        assert collection.responses[1].request_id == 2


class TestRequestedTokenText:
    """Tests for RequestedToken.text (BinarySecurityToken with certificate)."""

    def test_text_parses_certificate(self):
        """RequestedToken.text parses base64 certificate to PEM format."""
        # A minimal base64-encoded certificate content
        # (just for testing parsing)
        cert_b64 = "MIIB" + "A" * 100  # Simplified test data

        xml = f"""<RequestedSecurityToken xmlns="{NS_WST}">
        <BinarySecurityToken xmlns="{NS_WST_SECEXT}">{cert_b64}</BinarySecurityToken>
        </RequestedSecurityToken>"""  # noqa: E501
        element = ElementTree.fromstring(xml)
        token = RequestedToken(element)

        # CertificateConverter wraps in PEM format
        assert token.text is not None
        assert "-----BEGIN CERTIFICATE-----" in token.text
        assert "-----END CERTIFICATE-----" in token.text

    def test_text_returns_none_when_missing(self):
        """RequestedToken.text should return None when element is missing."""
        xml = f'<RequestedSecurityToken xmlns="{NS_WST}" />'
        element = ElementTree.fromstring(xml)
        token = RequestedToken(element)

        assert token.text is None

    def test_text_returns_string_type(self):
        """RequestedToken.text should return str type (PEM certificate)."""
        cert_b64 = "MIIB" + "A" * 100

        xml = f"""<RequestedSecurityToken xmlns="{NS_WST}">
        <BinarySecurityToken xmlns="{NS_WST_SECEXT}">{cert_b64}</BinarySecurityToken>
        </RequestedSecurityToken>"""  # noqa: E501
        element = ElementTree.fromstring(xml)
        token = RequestedToken(element)

        assert isinstance(token.text, str)


class TestRequestedTokenReference:
    """Tests for RequestedToken.token_reference chain access."""

    def test_token_reference_parsing(self):
        """RequestedToken should parse SecurityTokenReference child."""
        xml = f"""<RequestedSecurityToken xmlns="{NS_WST}">
        <SecurityTokenReference xmlns="{NS_WST_SECEXT}">
            <Reference URI="#cert-123" />
        </SecurityTokenReference>
        </RequestedSecurityToken>"""
        element = ElementTree.fromstring(xml)
        token = RequestedToken(element)

        assert token.token_reference is not None
        assert isinstance(token.token_reference, SecurityTokenReference)

    def test_token_reference_chain_access(self):
        """Test full chain: token_reference.reference.uri access.

        This is the access pattern used in service.py:135:
        response.requested_token.token_reference.reference.uri
        """
        xml = f"""<RequestedSecurityToken xmlns="{NS_WST}">
        <SecurityTokenReference xmlns="{NS_WST_SECEXT}">
            <Reference URI="#binary-token-456" />
        </SecurityTokenReference>
        </RequestedSecurityToken>"""
        element = ElementTree.fromstring(xml)
        token = RequestedToken(element)

        # Full chain access as used in service.py
        assert token.token_reference is not None
        assert token.token_reference.reference is not None
        assert token.token_reference.reference.uri == "#binary-token-456"

    def test_token_reference_returns_none_when_missing(self):
        """RequestedToken.token_reference should return None when missing."""
        xml = f'<RequestedSecurityToken xmlns="{NS_WST}" />'
        element = ElementTree.fromstring(xml)
        token = RequestedToken(element)

        assert token.token_reference is None


class TestSecurityTokenResponseRequestedToken:
    """Tests for SecurityTokenResponse.requested_token access."""

    def test_requested_token_parsing(self):
        """SecurityTokenResponse should parse RequestedSecurityToken child."""
        xml = f"""<RequestSecurityTokenResponse xmlns="{NS_WST}">
        <DispositionMessage xmlns="{NS_ENROLLMENT}">Issued</DispositionMessage>
        <RequestID xmlns="{NS_ENROLLMENT}">12345</RequestID>
        <RequestedSecurityToken>
            <BinarySecurityToken xmlns="{NS_WST_SECEXT}">MIIB{'A'*100}</BinarySecurityToken>
        </RequestedSecurityToken>
        </RequestSecurityTokenResponse>"""  # noqa: E501
        element = ElementTree.fromstring(xml)
        response = SecurityTokenResponse(element)

        assert response.requested_token is not None
        assert isinstance(response.requested_token, RequestedToken)

    def test_requested_token_text_access(self):
        """Test response.requested_token.text access pattern.

        This access pattern is used in service.py.
        """
        cert_b64 = "MIIB" + "A" * 100

        xml = f"""<RequestSecurityTokenResponse xmlns="{NS_WST}">
        <DispositionMessage xmlns="{NS_ENROLLMENT}">Issued</DispositionMessage>
        <RequestID xmlns="{NS_ENROLLMENT}">12345</RequestID>
        <RequestedSecurityToken>
            <BinarySecurityToken xmlns="{NS_WST_SECEXT}">{cert_b64}</BinarySecurityToken>
        </RequestedSecurityToken>
        </RequestSecurityTokenResponse>"""  # noqa: E501
        element = ElementTree.fromstring(xml)
        response = SecurityTokenResponse(element)

        # Access pattern from service.py:121
        token = response.requested_token
        assert token.text is not None
        assert "-----BEGIN CERTIFICATE-----" in token.text

    def test_requested_token_full_chain(self):
        """Test response.requested_token.token_reference.reference.uri.

        This reproduces the exact access pattern from service.py:135-136.
        """
        xml = f"""<RequestSecurityTokenResponse xmlns="{NS_WST}">
        <DispositionMessage xmlns="{NS_ENROLLMENT}">Pending</DispositionMessage>
        <RequestID xmlns="{NS_ENROLLMENT}">67890</RequestID>
        <RequestedSecurityToken>
            <SecurityTokenReference xmlns="{NS_WST_SECEXT}">
                <Reference URI="#pending-request-ref" />
            </SecurityTokenReference>
        </RequestedSecurityToken>
        </RequestSecurityTokenResponse>"""  # noqa: E501
        element = ElementTree.fromstring(xml)
        response = SecurityTokenResponse(element)

        # Exact access pattern from service.py:135-136
        token_ref = response.requested_token.token_reference
        assert token_ref is not None
        assert token_ref.reference is not None
        assert token_ref.reference.uri == "#pending-request-ref"


class TestTypePreservation:
    """Tests verifying that descriptors return correct runtime types.

    These tests ensure type safety is preserved through the descriptor
    chain, which is critical before adding type stubs.
    """

    def test_request_id_returns_int(self):
        """XMLValue with UnsignedIntegerConverter should return int."""
        xml = f"""<RequestSecurityTokenResponse xmlns="{NS_WST}">
        <DispositionMessage xmlns="{NS_ENROLLMENT}">Issued</DispositionMessage>
        <RequestID xmlns="{NS_ENROLLMENT}">42</RequestID>
        </RequestSecurityTokenResponse>"""
        element = ElementTree.fromstring(xml)
        response = SecurityTokenResponse(element)

        assert response.request_id == 42
        assert isinstance(response.request_id, int)

    def test_disposition_message_returns_str(self):
        """XMLValue with StringConverter should return str."""
        xml = f"""<RequestSecurityTokenResponse xmlns="{NS_WST}">
        <DispositionMessage xmlns="{NS_ENROLLMENT}">Issued</DispositionMessage>
        <RequestID xmlns="{NS_ENROLLMENT}">1</RequestID>
        </RequestSecurityTokenResponse>"""
        element = ElementTree.fromstring(xml)
        response = SecurityTokenResponse(element)

        assert response.disposition_message == "Issued"
        assert isinstance(response.disposition_message, str)

    def test_uri_attribute_returns_str(self):
        """XMLAttribute with StringConverter should return str."""
        xml = f'<Reference xmlns="{NS_WST_SECEXT}" URI="#token-id" />'
        element = ElementTree.fromstring(xml)
        ref = Reference(element)

        assert ref.uri == "#token-id"
        assert isinstance(ref.uri, str)

    def test_responses_returns_list(self):
        """XMLElementList should return a list-like object."""
        xml = f"""<RequestSecurityTokenResponseCollection xmlns="{NS_WST}">
        <RequestSecurityTokenResponse>
        <DispositionMessage xmlns="{NS_ENROLLMENT}">Issued</DispositionMessage>
        <RequestID xmlns="{NS_ENROLLMENT}">1</RequestID>
        </RequestSecurityTokenResponse>
        </RequestSecurityTokenResponseCollection>"""
        element = ElementTree.fromstring(xml)
        collection = SecurityTokenResponseCollection(element)

        assert collection.responses is not None
        # Should be indexable like a list
        assert collection.responses[0] is not None
        assert isinstance(collection.responses[0], SecurityTokenResponse)

    def test_nested_type_chain_preservation(self):
        """Verify types are preserved through nested XMLElement access."""
        xml = f"""<RequestSecurityTokenResponse xmlns="{NS_WST}">
        <DispositionMessage xmlns="{NS_ENROLLMENT}">Pending</DispositionMessage>
        <RequestID xmlns="{NS_ENROLLMENT}">999</RequestID>
        <RequestedSecurityToken>
            <SecurityTokenReference xmlns="{NS_WST_SECEXT}">
                <Reference URI="#ref-abc" />
            </SecurityTokenReference>
        </RequestedSecurityToken>
        </RequestSecurityTokenResponse>"""  # noqa: E501
        element = ElementTree.fromstring(xml)
        response = SecurityTokenResponse(element)

        # Verify each step in the chain has correct type
        assert isinstance(response, SecurityTokenResponse)
        assert isinstance(response.requested_token, RequestedToken)
        assert isinstance(
            response.requested_token.token_reference, SecurityTokenReference
        )
        assert isinstance(
            response.requested_token.token_reference.reference, Reference
        )
        assert isinstance(
            response.requested_token.token_reference.reference.uri, str
        )
