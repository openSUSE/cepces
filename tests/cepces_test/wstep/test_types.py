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
from xml.etree.ElementTree import QName
from cepces.wstep.types import SecurityTokenRequest
from cepces.wstep import (
    NS_WST_SECEXT,
    NS_WST,
    ENCODING_TYPE,
    VALUE_TYPE,
    TOKEN_TYPE,
    ISSUE_REQUEST_TYPE,
)


def test_security_token_request_has_the_right_types():
    """BinarySecurityToken must have EncodingType attribute.

    When requesting a certificate, IIS returns HTTP 500 with error:
    "The EncodingType is invalid." if the BinarySecurityToken element
    does not have the EncodingType attribute set.

    The EncodingType attribute is required by WS-Security spec and must be:
    http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd#base64binary
    """
    element = SecurityTokenRequest.create()

    # Find the Token type element
    token_type = element.find(f"{{{NS_WST}}}TokenType")
    assert token_type is not None, "TokenType element not found"
    assert (
        token_type.text == TOKEN_TYPE
    ), f"TokenType should be {TOKEN_TYPE}, got {token_type.text}"

    # Find the Request type element
    request_type = element.find(f"{{{NS_WST}}}RequestType")
    assert request_type is not None, "RequestType element not found"
    assert (
        request_type.text == ISSUE_REQUEST_TYPE
    ), f"RequestType should be {ISSUE_REQUEST_TYPE}, got {request_type.text}"

    # Find the BinarySecurityToken element
    token = element.find(f"{{{NS_WST_SECEXT}}}BinarySecurityToken")
    assert token is not None, "BinarySecurityToken element not found"

    # check element value type
    value_type = token.get(QName("ValueType"))
    assert value_type is not None, "ValueType attribute is missing"
    assert (
        value_type == VALUE_TYPE
    ), f"ValueType should be {VALUE_TYPE}, got {value_type}"

    # Check that EncodingType attribute is present and correct
    encoding_type = token.get(QName("EncodingType"))
    assert encoding_type is not None, "EncodingType attribute is missing"
    assert (
        encoding_type == ENCODING_TYPE
    ), f"EncodingType should be {ENCODING_TYPE}, got {encoding_type}"
