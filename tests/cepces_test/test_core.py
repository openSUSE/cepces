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
import datetime
import unittest
import logging
from xml.etree import ElementTree
from unittest.mock import Mock, patch, PropertyMock
import requests.exceptions
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import AuthorityInformationAccessOID, NameOID
from cepces import Base
from cepces.core import Service
from cepces.soap.service import SOAPFault
from cepces.xcep.types import GetPoliciesResponse

# GetPoliciesResponse with nil policies and CAs (no enrollment available)
GET_POLICIES_NIL_POLICIES_XML = b'<ns0:GetPoliciesResponse xmlns:ns0="http://schemas.microsoft.com/windows/pki/2009/01/enrollmentpolicy" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><ns0:response><ns0:policyID>{F803BF1A-EB36-42A4-973C-AF4555EB8782}</ns0:policyID><ns0:policyFriendlyName>My PKI</ns0:policyFriendlyName><ns0:nextUpdateHours>1</ns0:nextUpdateHours><ns0:policiesNotChanged xsi:nil="true" /><ns0:policies xsi:nil="true" /></ns0:response><ns0:cAs xsi:nil="true" /><ns0:oIDs xsi:nil="true" /></ns0:GetPoliciesResponse>'  # noqa: E501

# GetPoliciesResponse with empty CAs list (cAs present but no cA children)
GET_POLICIES_EMPTY_CAS_XML = b'<ns0:GetPoliciesResponse xmlns:ns0="http://schemas.microsoft.com/windows/pki/2009/01/enrollmentpolicy" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><ns0:response><ns0:policyID>{F803BF1A-EB36-42A4-973C-AF4555EB8782}</ns0:policyID><ns0:policyFriendlyName>My PKI</ns0:policyFriendlyName><ns0:nextUpdateHours>1</ns0:nextUpdateHours><ns0:policiesNotChanged xsi:nil="true" /><ns0:policies xsi:nil="true" /></ns0:response><ns0:cAs></ns0:cAs><ns0:oIDs xsi:nil="true" /></ns0:GetPoliciesResponse>'  # noqa: E501


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


def test_service_endpoints_with_empty_cas():
    """Tests that Service.endpoints handles an empty CAs list gracefully.

    When the AD CS server returns a GetPoliciesResponse with an empty
    '<ns0:cAs>' element (no <cA> children), accessing Service.endpoints
    should return None instead of raising IndexError.
    """
    element = ElementTree.fromstring(GET_POLICIES_EMPTY_CAS_XML)
    policies_response = GetPoliciesResponse(element)

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

        endpoints = service.endpoints

        assert endpoints is None


def test_service_certificate_chain_with_empty_cas():
    """Tests that Service.certificate_chain handles an empty CAs list.

    When the AD CS server returns a GetPoliciesResponse with an empty
    '<ns0:cAs>' element (no <cA> children), accessing Service.certificate_chain
    should return None instead of raising IndexError.  This is the crash
    reported in https://github.com/openSUSE/cepces/issues/8 for multi-forest
    AD setups.
    """
    element = ElementTree.fromstring(GET_POLICIES_EMPTY_CAS_XML)
    policies_response = GetPoliciesResponse(element)

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

        chain = service.certificate_chain

        assert chain is None


# ---------------------------------------------------------------------------
# Helper for _resolve_chain tests
# ---------------------------------------------------------------------------

_AIA_URI = "http://ca.example.com/root.crt"


def _make_test_chain():
    """Generate a root CA + leaf cert pair for _resolve_chain tests.

    Returns (root_cert, root_pem, root_der, leaf_cert, leaf_pem, leaf_der).
    The leaf has an AIA extension pointing to _AIA_URI.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    later = now + datetime.timedelta(days=365)

    root_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend(),
    )
    root_name = x509.Name(
        [x509.NameAttribute(NameOID.COMMON_NAME, "Test Root CA")]
    )
    root_cert = (
        x509.CertificateBuilder()
        .subject_name(root_name)
        .issuer_name(root_name)
        .public_key(root_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(later)
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        )
        .sign(root_key, hashes.SHA256(), default_backend())
    )
    root_pem = root_cert.public_bytes(serialization.Encoding.PEM)
    root_der = root_cert.public_bytes(serialization.Encoding.DER)

    leaf_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend(),
    )
    leaf_name = x509.Name(
        [x509.NameAttribute(NameOID.COMMON_NAME, "Test Leaf")]
    )
    leaf_cert = (
        x509.CertificateBuilder()
        .subject_name(leaf_name)
        .issuer_name(root_name)
        .public_key(leaf_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(later)
        .add_extension(
            x509.AuthorityInformationAccess(
                [
                    x509.AccessDescription(
                        AuthorityInformationAccessOID.CA_ISSUERS,
                        x509.UniformResourceIdentifier(_AIA_URI),
                    ),
                ]
            ),
            critical=False,
        )
        .sign(root_key, hashes.SHA256(), default_backend())
    )
    leaf_pem = leaf_cert.public_bytes(serialization.Encoding.PEM)
    leaf_der = leaf_cert.public_bytes(serialization.Encoding.DER)

    return root_cert, root_pem, root_der, leaf_cert, leaf_pem, leaf_der


def _make_service_with_mock_session():
    """Return (service, mock_session) with XCEPService and session patched."""
    mock_config = Mock()
    mock_config.endpoint_type = "Policy"
    mock_config.endpoint = "https://example.com/CEP"
    mock_config.auth = Mock()
    mock_config.cas = None
    mock_config.openssl_ciphers = None

    mock_session = Mock()

    with (
        patch("cepces.core.XCEPService") as mock_xcep_class,
        patch("cepces.core.create_session", return_value=mock_session),
    ):
        mock_xcep = Mock()
        mock_xcep.get_policies.return_value = Mock()
        mock_xcep_class.return_value = mock_xcep

        service = Service(mock_config)

    return service, mock_session


# ---------------------------------------------------------------------------
# _resolve_chain tests
# ---------------------------------------------------------------------------


def test_resolve_chain_pem_string_self_signed():
    """_resolve_chain accepts a PEM string (the line-202 call-site format)."""
    root_cert, root_pem, _root_der, *_ = _make_test_chain()
    service, _ = _make_service_with_mock_session()

    result = service._resolve_chain(root_pem.decode())

    assert len(result) == 1
    assert result[0].subject == root_cert.subject


def test_resolve_chain_pem_bytes_self_signed():
    """_resolve_chain accepts PEM bytes."""
    root_cert, root_pem, _root_der, *_ = _make_test_chain()
    service, _ = _make_service_with_mock_session()

    result = service._resolve_chain(root_pem)

    assert len(result) == 1
    assert result[0].subject == root_cert.subject


def test_resolve_chain_der_bytes_self_signed():
    """_resolve_chain accepts raw DER bytes for a self-signed cert."""
    root_cert, _root_pem, root_der, *_ = _make_test_chain()
    service, _ = _make_service_with_mock_session()

    result = service._resolve_chain(root_der)

    assert len(result) == 1
    assert result[0].subject == root_cert.subject


def test_resolve_chain_self_signed_stops_recursion():
    """_resolve_chain stops at a self-signed cert without any HTTP call."""
    _root_cert, root_pem, _root_der, *_ = _make_test_chain()
    service, mock_session = _make_service_with_mock_session()

    service._resolve_chain(root_pem)

    mock_session.get.assert_not_called()


def test_resolve_chain_aia_with_pem_response():
    """_resolve_chain follows AIA and handles a PEM-encoded intermediate."""
    root_cert, root_pem, _root_der, leaf_cert, leaf_pem, _ = _make_test_chain()
    service, mock_session = _make_service_with_mock_session()

    mock_response = Mock()
    mock_response.content = root_pem
    mock_session.get.return_value = mock_response

    result = service._resolve_chain(leaf_pem)

    mock_session.get.assert_called_once_with(_AIA_URI)
    assert len(result) == 2
    assert result[0].subject == leaf_cert.subject
    assert result[1].subject == root_cert.subject


def test_resolve_chain_aia_with_der_response():
    """_resolve_chain follows AIA and handles a DER-encoded intermediate.

    This is the bug from https://github.com/openSUSE/cepces/issues/46:
    using r.content (bytes) instead of r.text (str) preserves binary DER.
    """
    root_cert, _root_pem, root_der, leaf_cert, leaf_pem, _ = _make_test_chain()
    service, mock_session = _make_service_with_mock_session()

    mock_response = Mock()
    mock_response.content = root_der
    mock_session.get.return_value = mock_response

    result = service._resolve_chain(leaf_pem)

    mock_session.get.assert_called_once_with(_AIA_URI)
    assert len(result) == 2
    assert result[0].subject == leaf_cert.subject
    assert result[1].subject == root_cert.subject


# ---------------------------------------------------------------------------
# _request_cep failover tests
# ---------------------------------------------------------------------------


def _make_service_for_failover():
    """Return a Service in Policy mode without mocking endpoints."""
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
        mock_xcep.get_policies.return_value = Mock()
        mock_xcep_class.return_value = mock_xcep

        service = Service(mock_config)

    return service, mock_config


def _make_endpoint(url: str) -> Mock:
    ep = Mock()
    ep.url = url
    ep.renewal_only = False
    return ep


def test_request_cep_failover_to_second_endpoint():
    """_request_cep retries the next endpoint when the first fails."""
    service, _mock_config = _make_service_for_failover()

    ep1 = _make_endpoint("https://ces1.example.com/CES")
    ep2 = _make_endpoint("https://ces2.example.com/CES")
    mock_response = Mock()

    connection_error = requests.exceptions.ConnectionError("refused")

    with (
        patch.object(
            type(service), "endpoints", new_callable=PropertyMock
        ) as mock_endpoints,
        patch.object(service, "_request_ces") as mock_request_ces,
    ):
        mock_endpoints.return_value = [ep1, ep2]
        mock_request_ces.side_effect = [connection_error, mock_response]

        result = service._request_cep(Mock())

    assert result is mock_response
    assert mock_request_ces.call_count == 2


def test_request_cep_all_endpoints_fail():
    """_request_cep re-raises the last exception when all endpoints fail."""
    service, _mock_config = _make_service_for_failover()

    ep1 = _make_endpoint("https://ces1.example.com/CES")
    ep2 = _make_endpoint("https://ces2.example.com/CES")

    error1 = requests.exceptions.ConnectionError("refused ces1")
    error2 = requests.exceptions.ConnectionError("refused ces2")

    with (
        patch.object(
            type(service), "endpoints", new_callable=PropertyMock
        ) as mock_endpoints,
        patch.object(service, "_request_ces") as mock_request_ces,
    ):
        mock_endpoints.return_value = [ep1, ep2]
        mock_request_ces.side_effect = [error1, error2]

        raised = None
        try:
            service._request_cep(Mock())
        except requests.exceptions.ConnectionError as e:
            raised = e

    assert raised is error2
    assert mock_request_ces.call_count == 2


def test_request_cep_soap_fault_does_not_failover():
    """_request_cep propagates SOAPFault without trying next endpoint."""
    service, _mock_config = _make_service_for_failover()

    ep1 = _make_endpoint("https://ces1.example.com/CES")
    ep2 = _make_endpoint("https://ces2.example.com/CES")

    mock_fault = Mock()
    mock_fault.code.value = "env:Receiver"
    mock_fault.code.subcode = None
    mock_fault.reason.text = "Request denied"

    with (
        patch.object(
            type(service), "endpoints", new_callable=PropertyMock
        ) as mock_endpoints,
        patch.object(service, "_request_ces") as mock_request_ces,
    ):
        mock_endpoints.return_value = [ep1, ep2]
        mock_request_ces.side_effect = SOAPFault(mock_fault)

        raised = None
        try:
            service._request_cep(Mock())
        except SOAPFault as e:
            raised = e

    assert raised is not None
    assert mock_request_ces.call_count == 1


def test_request_cep_single_endpoint_success():
    """_request_cep returns the response when the single endpoint succeeds."""
    service, _mock_config = _make_service_for_failover()

    ep = _make_endpoint("https://ces1.example.com/CES")
    mock_response = Mock()

    with (
        patch.object(
            type(service), "endpoints", new_callable=PropertyMock
        ) as mock_endpoints,
        patch.object(service, "_request_ces") as mock_request_ces,
    ):
        mock_endpoints.return_value = [ep]
        mock_request_ces.return_value = mock_response

        result = service._request_cep(Mock())

    assert result is mock_response
    assert mock_request_ces.call_count == 1


def test_request_cep_no_endpoints_returns_none():
    """_request_cep returns None when no endpoints match."""
    service, _mock_config = _make_service_for_failover()

    with patch.object(
        type(service), "endpoints", new_callable=PropertyMock
    ) as mock_endpoints:
        mock_endpoints.return_value = []

        result = service._request_cep(Mock())

    assert result is None
