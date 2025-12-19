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
from unittest.mock import Mock
from xml.etree import ElementTree
from cepces import __title__, __version__
from cepces.certmonger.core import Result as CertmongerResult
import cepces.certmonger.operation as CertmongerOperations
from cepces.xcep.types import GetPoliciesResponse
from cryptography import x509
from cryptography.hazmat.backends import default_backend
import io


def test_get_default_template_call():
    """Tests the GetDefaultTemplate operation"""
    out = io.StringIO()
    operation = CertmongerOperations.GetDefaultTemplate(None, out=out)
    operation()

    assert out.getvalue() == ""


def test_identify_call():
    """Tests the Identity operation"""
    out = io.StringIO()
    operation = CertmongerOperations.Identify(None, out=out)
    operation()

    assert out.getvalue() == "{} {}\n".format(__title__, __version__)


# Real certificate from MARS-ROOT-CA for testing
MARS_ROOT_CA_PEM = """-----BEGIN CERTIFICATE-----
MIIFrTCCA5WgAwIBAgIQb7gIsLLyR51KVoyagCO2ljANBgkqhkiG9w0BAQ0FADBd
MRQwEgYKCZImiZPyLGQBGRYEc2l0ZTEYMBYGCgmSJomT8ixkARkWCG1pbGt5d2F5
MRQwEgYKCZImiZPyLGQBGRYEbWFyczEVMBMGA1UEAxMMTUFSUy1ST09ULUNBMB4X
DTI1MDYzMDA4MTQzNFoXDTMwMDYzMDA4MjQzM1owXTEUMBIGCgmSJomT8ixkARkW
BHNpdGUxGDAWBgoJkiaJk/IsZAEZFghtaWxreXdheTEUMBIGCgmSJomT8ixkARkW
BG1hcnMxFTATBgNVBAMTDE1BUlMtUk9PVC1DQTCCAiIwDQYJKoZIhvcNAQEBBQAD
ggIPADCCAgoCggIBAM7E6RzfKHgzJBgKDv+f3YIWGD25K9Uk7ZYfvI9pywO4Eaj4
ER1DBDZGKwx3wElNW/pS45kza4zHgZhhHHImMyXKKoH/4+NCsW+F+KKS9i/EwHeO
Ki01/KI9BWhS9kiCvJ9e1ir3HOkcEtROTOt+vdncNDbHSQ9MlkZA9V1oCT8gAH1W
1knhvoMxnIp+rS7/MKnNiNTiIgEUHyau/MpzzeJb2GE0NWlfKdxAmvYJp6SDwIqV
AhSXm5jQ29ByFLfyz2jaRyJknwdskg8h9lGoPcWSq4iT70YVFxdRhzm0lo3Ag98T
J/RGIn0Gd5TTterjzJdNaU3ugIbssILIG7iVB68jonrhVaDWiEcF8NCz4/0XLcri
CpO4I1gOEgJp5OulHs/8ZVCBSTXbkh2640+bgzO4NaqaJZJHwTiy10nw1+VsVa7b
S9jk5OsTopBm6FTewa+NylRpK6V+kohg0P2fmcbOqSTtAvUB4I0EtbnQu5qvlw3b
VeUbn1jHWZ3lTPTKRoz5Bq9MUFbYJAIOg3KNdk+OTZkQqiHbUf7NqNMq6UTqrjec
9nnMj1ngD7OOaddExLtbfkrZ88gfYJLGt71e8tzAKMrPQ0p+WJ536uPGVOFChM3o
y6YeUpExZirK+aymzjbZQlRxlCTtFJgJoz3AqmUYFPXisOtWy1p8SYsxooX9AgMB
AAGjaTBnMBMGCSsGAQQBgjcUAgQGHgQAQwBBMA4GA1UdDwEB/wQEAwIBhjAPBgNV
HRMBAf8EBTADAQH/MB0GA1UdDgQWBBTsrV5HZN1O6EYT6YUp9TpQymsGljAQBgkr
BgEEAYI3FQEEAwIBADANBgkqhkiG9w0BAQ0FAAOCAgEAesNDznHL8SKc1yY+p7rB
xX4zqZxlcr9MFMmoaYrJR2CopVH3R5G++AkN1JOgZlJnoD0E3hQqwGmWjkLv/k94
uDcWIuPsMy4KAsyFY3+8z6zs+dNaue6R2n56zH0Om/QgEfjokZv7fOJI2zBf5SZ8
6xQBehoL9UIst0A+Mey8TRYzZX6s4dZXudelr7wu0KdRbFZTYB/j5mZx/vOfow1o
sEnr0yoIeh9Yp79hjukyGBGtUpmTFoBNQwWEpjOkJ50Q+TqNOVOwNYls4pVwkYx+
EwHTrDFEAFUtCp0M9rwWJ6LzqypsbyWtFFD38q6QY59rUv/m5m7AEMrHJo0yYaYO
ce7jqrG5d7RXBHSDKnYpBXzsqvz3oqXLH9H3ur+52CzqLs7hONnlk9C7blnCZFwM
CBhXRP0PtUO2+t8XJpXeMfnVNmgJmKq1+CT78/4T4wINEMhhsONpi0v0IptRethH
JknfZ0QYWMGEMxhG3KxRVK+LCqDxw5UCPmtSxnB9h5aP5NIzhq2wLMNgfW53u+Kr
rhdocTcVwus379oVOtStnNI0vX0tCZ/t8DzzxlMiAhXnyKl/y8kt/5Z8o0T0/3Pj
GdTdz9+3Fdhxf3uYQ2MGSUKTy4Bb2zJZLfKWNYmAbyQ3PadhztqU5DNkAh8Nksvq
KNALyDR9LeTgyB0+TY69kSg=
-----END CERTIFICATE-----"""


def test_fetch_roots_with_single_ca():
    """Tests the FetchRoots operation with a single CA certificate."""
    # Load the real certificate
    cert = x509.load_pem_x509_certificate(
        MARS_ROOT_CA_PEM.encode(), default_backend()
    )

    # Mock the service with certificate_chain returning the certificate
    mock_service = Mock()
    mock_service.certificate_chain = [cert]

    out = io.StringIO()
    operation = CertmongerOperations.FetchRoots(mock_service, out=out)
    result = operation()

    output = out.getvalue()

    # Verify the output contains the CA name
    assert "MARS-ROOT-CA" in output

    # Verify the output contains the PEM certificate
    assert "-----BEGIN CERTIFICATE-----" in output
    assert "-----END CERTIFICATE-----" in output

    # Verify the return code
    assert result == CertmongerResult.DEFAULT


def test_fetch_roots_with_no_cas():
    """Tests the FetchRoots operation when no CAs are available."""
    # Mock the service with certificate_chain returning None
    mock_service = Mock()
    mock_service.certificate_chain = None

    out = io.StringIO()
    operation = CertmongerOperations.FetchRoots(mock_service, out=out)
    result = operation()

    # Output should be empty
    assert out.getvalue() == "\n"

    # Verify the return code
    assert result == CertmongerResult.DEFAULT


# Raw XML response from AD CS server (captured from debug logs)
GET_POLICIES_RESPONSE_XML = b'<ns0:GetPoliciesResponse xmlns:ns0="http://schemas.microsoft.com/windows/pki/2009/01/enrollmentpolicy" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><ns0:response><ns0:policyID>{DA239A97-1289-4B14-924F-B318D56ED254}</ns0:policyID><ns0:policyFriendlyName /><ns0:nextUpdateHours>8</ns0:nextUpdateHours><ns0:policiesNotChanged xsi:nil="true" /><ns0:policies><ns0:policy><ns0:policyOIDReference>13</ns0:policyOIDReference><ns0:cAs><ns0:cAReference>0</ns0:cAReference></ns0:cAs><ns0:attributes><ns0:commonName>Machine</ns0:commonName><ns0:policySchema>1</ns0:policySchema><ns0:certificateValidity><ns0:validityPeriodSeconds>31536000</ns0:validityPeriodSeconds><ns0:renewalPeriodSeconds>3628800</ns0:renewalPeriodSeconds></ns0:certificateValidity><ns0:permission><ns0:enroll>true</ns0:enroll><ns0:autoEnroll>false</ns0:autoEnroll></ns0:permission><ns0:privateKeyAttributes><ns0:minimalKeyLength>2048</ns0:minimalKeyLength><ns0:keySpec>1</ns0:keySpec><ns0:keyUsageProperty xsi:nil="true" /><ns0:permissions xsi:nil="true" /><ns0:algorithmOIDReference xsi:nil="true" /><ns0:cryptoProviders><ns0:provider>Microsoft RSA SChannel Cryptographic Provider</ns0:provider></ns0:cryptoProviders></ns0:privateKeyAttributes><ns0:revision><ns0:majorRevision>5</ns0:majorRevision><ns0:minorRevision>1</ns0:minorRevision></ns0:revision><ns0:supersededPolicies xsi:nil="true" /><ns0:privateKeyFlags>0</ns0:privateKeyFlags><ns0:subjectNameFlags>402653184</ns0:subjectNameFlags><ns0:enrollmentFlags>0</ns0:enrollmentFlags><ns0:generalFlags>66144</ns0:generalFlags><ns0:hashAlgorithmOIDReference xsi:nil="true" /><ns0:rARequirements xsi:nil="true" /><ns0:keyArchivalAttributes xsi:nil="true" /><ns0:extensions><ns0:extension><ns0:oIDReference>5</ns0:oIDReference><ns0:critical>false</ns0:critical><ns0:value>Hg4ATQBhAGMAaABpAG4AZQ==</ns0:value></ns0:extension></ns0:extensions></ns0:attributes></ns0:policy></ns0:policies></ns0:response><ns0:cAs><ns0:cA><ns0:uris><ns0:cAURI><ns0:clientAuthentication>2</ns0:clientAuthentication><ns0:uri>https://win-ca01.mars.milkyway.site/MARS-ROOT-CA_CES_Kerberos/service.svc/CES</ns0:uri><ns0:priority>1</ns0:priority><ns0:renewalOnly>false</ns0:renewalOnly></ns0:cAURI></ns0:uris><ns0:certificate>MIIFrTCCA5WgAwIBAgIQb7gIsLLyR51KVoyagCO2ljANBgkqhkiG9w0BAQ0FADBdMRQwEgYKCZImiZPyLGQBGRYEc2l0ZTEYMBYGCgmSJomT8ixkARkWCG1pbGt5d2F5MRQwEgYKCZImiZPyLGQBGRYEbWFyczEVMBMGA1UEAxMMTUFSUy1ST09ULUNBMB4XDTI1MDYzMDA4MTQzNFoXDTMwMDYzMDA4MjQzM1owXTEUMBIGCgmSJomT8ixkARkWBHNpdGUxGDAWBgoJkiaJk/IsZAEZFghtaWxreXdheTEUMBIGCgmSJomT8ixkARkWBG1hcnMxFTATBgNVBAMTDE1BUlMtUk9PVC1DQTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAM7E6RzfKHgzJBgKDv+f3YIWGD25K9Uk7ZYfvI9pywO4Eaj4ER1DBDZGKwx3wElNW/pS45kza4zHgZhhHHImMyXKKoH/4+NCsW+F+KKS9i/EwHeOKi01/KI9BWhS9kiCvJ9e1ir3HOkcEtROTOt+vdncNDbHSQ9MlkZA9V1oCT8gAH1W1knhvoMxnIp+rS7/MKnNiNTiIgEUHyau/MpzzeJb2GE0NWlfKdxAmvYJp6SDwIqVAhSXm5jQ29ByFLfyz2jaRyJknwdskg8h9lGoPcWSq4iT70YVFxdRhzm0lo3Ag98TJ/RGIn0Gd5TTterjzJdNaU3ugIbssILIG7iVB68jonrhVaDWiEcF8NCz4/0XLcriCpO4I1gOEgJp5OulHs/8ZVCBSTXbkh2640+bgzO4NaqaJZJHwTiy10nw1+VsVa7bS9jk5OsTopBm6FTewa+NylRpK6V+kohg0P2fmcbOqSTtAvUB4I0EtbnQu5qvlw3bVeUbn1jHWZ3lTPTKRoz5Bq9MUFbYJAIOg3KNdk+OTZkQqiHbUf7NqNMq6UTqrjec9nnMj1ngD7OOaddExLtbfkrZ88gfYJLGt71e8tzAKMrPQ0p+WJ536uPGVOFChM3oy6YeUpExZirK+aymzjbZQlRxlCTtFJgJoz3AqmUYFPXisOtWy1p8SYsxooX9AgMBAAGjaTBnMBMGCSsGAQQBgjcUAgQGHgQAQwBBMA4GA1UdDwEB/wQEAwIBhjAPBgNVHRMBAf8EBTADAQH/MB0GA1UdDgQWBBTsrV5HZN1O6EYT6YUp9TpQymsGljAQBgkrBgEEAYI3FQEEAwIBADANBgkqhkiG9w0BAQ0FAAOCAgEAesNDznHL8SKc1yY+p7rBxX4zqZxlcr9MFMmoaYrJR2CopVH3R5G++AkN1JOgZlJnoD0E3hQqwGmWjkLv/k94uDcWIuPsMy4KAsyFY3+8z6zs+dNaue6R2n56zH0Om/QgEfjokZv7fOJI2zBf5SZ86xQBehoL9UIst0A+Mey8TRYzZX6s4dZXudelr7wu0KdRbFZTYB/j5mZx/vOfow1osEnr0yoIeh9Yp79hjukyGBGtUpmTFoBNQwWEpjOkJ50Q+TqNOVOwNYls4pVwkYx+EwHTrDFEAFUtCp0M9rwWJ6LzqypsbyWtFFD38q6QY59rUv/m5m7AEMrHJo0yYaYOce7jqrG5d7RXBHSDKnYpBXzsqvz3oqXLH9H3ur+52CzqLs7hONnlk9C7blnCZFwMCBhXRP0PtUO2+t8XJpXeMfnVNmgJmKq1+CT78/4T4wINEMhhsONpi0v0IptRethHJknfZ0QYWMGEMxhG3KxRVK+LCqDxw5UCPmtSxnB9h5aP5NIzhq2wLMNgfW53u+KrrhdocTcVwus379oVOtStnNI0vX0tCZ/t8DzzxlMiAhXnyKl/y8kt/5Z8o0T0/3PjGdTdz9+3Fdhxf3uYQ2MGSUKTy4Bb2zJZLfKWNYmAbyQ3PadhztqU5DNkAh8NksvqKNALyDR9LeTgyB0+TY69kSg=</ns0:certificate><ns0:enrollPermission>true</ns0:enrollPermission><ns0:cAReferenceID>0</ns0:cAReferenceID></ns0:cA></ns0:cAs><ns0:oIDs><ns0:oID><ns0:value>1.3.6.1.5.5.7.3.2</ns0:value><ns0:group>7</ns0:group><ns0:oIDReferenceID>4</ns0:oIDReferenceID><ns0:defaultName>Client Authentication</ns0:defaultName></ns0:oID></ns0:oIDs></ns0:GetPoliciesResponse>'  # noqa: E501


def test_fetch_roots_from_xml_response():
    """Tests the FetchRoots operation by parsing actual XML from AD CS.

    This test parses the GetPoliciesResponse XML captured from a real AD CS
    server and verifies that FetchRoots correctly extracts the CA certificate.
    """
    # Parse the XML response
    element = ElementTree.fromstring(GET_POLICIES_RESPONSE_XML)
    policies_response = GetPoliciesResponse(element)

    # Verify we can extract the CA
    assert policies_response.cas is not None
    assert len(policies_response.cas) == 1

    # Get the certificate from the CA
    ca = policies_response.cas[0]
    cert_pem = ca.certificate

    # Verify it's a valid PEM certificate
    assert cert_pem is not None
    assert "-----BEGIN CERTIFICATE-----" in cert_pem
    assert "-----END CERTIFICATE-----" in cert_pem

    # Load and verify the certificate
    cert = x509.load_pem_x509_certificate(cert_pem.encode(), default_backend())

    # Mock the service to return this certificate via certificate_chain
    mock_service = Mock()
    mock_service.certificate_chain = [cert]

    out = io.StringIO()
    operation = CertmongerOperations.FetchRoots(mock_service, out=out)
    result = operation()

    output = out.getvalue()

    # Verify the output contains the CA name from the certificate
    assert "MARS-ROOT-CA" in output

    # Verify the output contains the PEM certificate
    assert "-----BEGIN CERTIFICATE-----" in output
    assert "-----END CERTIFICATE-----" in output

    # Verify the return code
    assert result == CertmongerResult.DEFAULT
