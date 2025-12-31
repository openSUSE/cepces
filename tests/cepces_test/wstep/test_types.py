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
from cepces.wstep.types import SecurityTokenRequest
from cepces.wstep import NS_WST, NS_WST_SECEXT, NS_WST_UTILITY
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
