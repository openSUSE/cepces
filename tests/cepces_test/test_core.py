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
import unittest
import logging
from xml.etree import ElementTree
from unittest.mock import Mock, patch
from cepces import Base
from cepces.core import Service
from cepces.xcep.types import GetPoliciesResponse


# GetPoliciesResponse with nil policies and CAs (no enrollment available)
GET_POLICIES_NIL_POLICIES_XML = b'<ns0:GetPoliciesResponse xmlns:ns0="http://schemas.microsoft.com/windows/pki/2009/01/enrollmentpolicy" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><ns0:response><ns0:policyID>{F803BF1A-EB36-42A4-973C-AF4555EB8782}</ns0:policyID><ns0:policyFriendlyName>My PKI</ns0:policyFriendlyName><ns0:nextUpdateHours>1</ns0:nextUpdateHours><ns0:policiesNotChanged xsi:nil="true" /><ns0:policies xsi:nil="true" /></ns0:response><ns0:cAs xsi:nil="true" /><ns0:oIDs xsi:nil="true" /></ns0:GetPoliciesResponse>'  # noqa: E501


class TestBase(unittest.TestCase):
    """Tests the Base class"""

    def test_default_logger(self):
        """Test with default logger"""
        base = Base()

        self.assertIsNotNone(base._logger)

    def test_supplied_logger(self):
        """Test with supplied logger"""
        logger = logging.getLogger("Test")
        base = Base(logger=logger)

        self.assertIsNotNone(base._logger)
        self.assertIs(base._logger, logger)


def test_service_templates_with_nil_policies():
    """Tests that Service.templates handles nil policies gracefully.

    When the AD CS server returns a GetPoliciesResponse with
    '<ns0:policies xsi:nil="true" />', accessing Service.templates
    should return None instead of raising TypeError.
    """
    # Parse the XML response with nil policies
    element = ElementTree.fromstring(GET_POLICIES_NIL_POLICIES_XML)
    policies_response = GetPoliciesResponse(element)

    # Create a mock Service that has the nil policies response
    mock_config = Mock()
    mock_config.endpoint_type = "Policy"
    mock_config.endpoint = "https://example.com/CEP"
    mock_config.auth = Mock()
    mock_config.cas = None
    mock_config.openssl_ciphers = None

    # We need to patch the XCEPService to avoid actual network calls
    # and return our nil policies response
    with (
        patch("cepces.core.XCEPService") as mock_xcep_class,
        patch("cepces.core.create_session"),
    ):
        mock_xcep = Mock()
        mock_xcep.get_policies.return_value = policies_response
        mock_xcep_class.return_value = mock_xcep

        service = Service(mock_config)

        # This should return None, but currently raises TypeError
        # because it tries to iterate over None
        templates = service.templates

        assert templates is None


def test_service_endpoints_with_nil_cas():
    """Tests that Service.endpoints handles nil CAs gracefully.

    When the AD CS server returns a GetPoliciesResponse with
    '<ns0:cAs xsi:nil="true" />', accessing Service.endpoints
    should return None instead of raising TypeError.
    """
    # Parse the XML response with nil CAs
    element = ElementTree.fromstring(GET_POLICIES_NIL_POLICIES_XML)
    policies_response = GetPoliciesResponse(element)

    # Create a mock Service that has the nil CAs response
    mock_config = Mock()
    mock_config.endpoint_type = "Policy"
    mock_config.endpoint = "https://example.com/CEP"
    mock_config.auth = Mock()
    mock_config.cas = None
    mock_config.openssl_ciphers = None

    with (
        patch("cepces.core.XCEPService") as mock_xcep_class,
        patch("cepces.core.create_session"),
    ):
        mock_xcep = Mock()
        mock_xcep.get_policies.return_value = policies_response
        mock_xcep_class.return_value = mock_xcep

        service = Service(mock_config)

        # This should return None, but currently raises TypeError
        # because it tries to iterate over None
        endpoints = service.endpoints

        assert endpoints is None
