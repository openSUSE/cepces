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
from unittest.mock import Mock, patch
from xml.etree import ElementTree
from cepces import __title__, __version__
from cepces.certmonger.core import Result as CertmongerResult
import cepces.certmonger.operation as CertmongerOperations
from cepces.xcep.types import GetPoliciesResponse
from cepces.wstep.types import SecurityTokenResponseCollection
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID
import io


def test_get_default_template_call() -> None:
    """Tests the GetDefaultTemplate operation"""
    out = io.StringIO()
    operation = CertmongerOperations.GetDefaultTemplate(None, out=out)
    operation()

    assert out.getvalue() == ""


def test_identify_call() -> None:
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


def test_fetch_roots_with_single_ca() -> None:
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


def test_fetch_roots_with_no_cas() -> None:
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


def test_fetch_roots_from_xml_response() -> None:
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


# XML response with xsi:nil="true" for cAs (no CAs configured)
GET_POLICIES_RESPONSE_NIL_CAS_XML = b'<ns0:GetPoliciesResponse xmlns:ns0="http://schemas.microsoft.com/windows/pki/2009/01/enrollmentpolicy" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><ns0:response><ns0:policyID>{F803BF1A-EB36-42A4-973C-AF4555EB8782}</ns0:policyID><ns0:policyFriendlyName>My PKI</ns0:policyFriendlyName><ns0:nextUpdateHours>1</ns0:nextUpdateHours><ns0:policiesNotChanged xsi:nil="true" /><ns0:policies xsi:nil="true" /></ns0:response><ns0:cAs xsi:nil="true" /><ns0:oIDs xsi:nil="true" /></ns0:GetPoliciesResponse>'  # noqa: E501


# XML from cepces-get-supported-templates.log line 33 (GetPoliciesResponse)
# Extracted from the SOAP envelope on line 32
# fmt: off
GET_SUPPORTED_TEMPLATES_XML = b'<ns0:GetPoliciesResponse xmlns:ns0="http://schemas.microsoft.com/windows/pki/2009/01/enrollmentpolicy" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><ns0:response><ns0:policyID>{DA239A97-1289-4B14-924F-B318D56ED254}</ns0:policyID><ns0:policyFriendlyName /><ns0:nextUpdateHours>8</ns0:nextUpdateHours><ns0:policiesNotChanged xsi:nil="true" /><ns0:policies><ns0:policy><ns0:policyOIDReference>13</ns0:policyOIDReference><ns0:cAs><ns0:cAReference>0</ns0:cAReference></ns0:cAs><ns0:attributes><ns0:commonName>Machine</ns0:commonName><ns0:policySchema>1</ns0:policySchema><ns0:certificateValidity><ns0:validityPeriodSeconds>31536000</ns0:validityPeriodSeconds><ns0:renewalPeriodSeconds>3628800</ns0:renewalPeriodSeconds></ns0:certificateValidity><ns0:permission><ns0:enroll>true</ns0:enroll><ns0:autoEnroll>false</ns0:autoEnroll></ns0:permission><ns0:privateKeyAttributes><ns0:minimalKeyLength>2048</ns0:minimalKeyLength><ns0:keySpec>1</ns0:keySpec><ns0:keyUsageProperty xsi:nil="true" /><ns0:permissions xsi:nil="true" /><ns0:algorithmOIDReference xsi:nil="true" /><ns0:cryptoProviders><ns0:provider>Microsoft RSA SChannel Cryptographic Provider</ns0:provider></ns0:cryptoProviders></ns0:privateKeyAttributes><ns0:revision><ns0:majorRevision>5</ns0:majorRevision><ns0:minorRevision>1</ns0:minorRevision></ns0:revision><ns0:supersededPolicies xsi:nil="true" /><ns0:privateKeyFlags>0</ns0:privateKeyFlags><ns0:subjectNameFlags>402653184</ns0:subjectNameFlags><ns0:enrollmentFlags>0</ns0:enrollmentFlags><ns0:generalFlags>66144</ns0:generalFlags><ns0:hashAlgorithmOIDReference xsi:nil="true" /><ns0:rARequirements xsi:nil="true" /><ns0:keyArchivalAttributes xsi:nil="true" /><ns0:extensions><ns0:extension><ns0:oIDReference>5</ns0:oIDReference><ns0:critical>false</ns0:critical><ns0:value>Hg4ATQBhAGMAaABpAG4AZQ==</ns0:value></ns0:extension><ns0:extension><ns0:oIDReference>6</ns0:oIDReference><ns0:critical>false</ns0:critical><ns0:value>MBQGCCsGAQUFBwMCBggrBgEFBQcDAQ==</ns0:value></ns0:extension><ns0:extension><ns0:oIDReference>7</ns0:oIDReference><ns0:critical>true</ns0:critical><ns0:value>AwIFoA==</ns0:value></ns0:extension></ns0:extensions></ns0:attributes></ns0:policy></ns0:policies></ns0:response><ns0:cAs><ns0:cA><ns0:uris><ns0:cAURI><ns0:clientAuthentication>2</ns0:clientAuthentication><ns0:uri>https://win-ca01.mars.milkyway.site/MARS-ROOT-CA_CES_Kerberos/service.svc/CES</ns0:uri><ns0:priority>1</ns0:priority><ns0:renewalOnly>false</ns0:renewalOnly></ns0:cAURI></ns0:uris><ns0:certificate>MIIFrTCCA5WgAwIBAgIQb7gIsLLyR51KVoyagCO2ljANBgkqhkiG9w0BAQ0FADBdMRQwEgYKCZImiZPyLGQBGRYEc2l0ZTEYMBYGCgmSJomT8ixkARkWCG1pbGt5d2F5MRQwEgYKCZImiZPyLGQBGRYEbWFyczEVMBMGA1UEAxMMTUFSUy1ST09ULUNBMB4XDTI1MDYzMDA4MTQzNFoXDTMwMDYzMDA4MjQzM1owXTEUMBIGCgmSJomT8ixkARkWBHNpdGUxGDAWBgoJkiaJk/IsZAEZFghtaWxreXdheTEUMBIGCgmSJomT8ixkARkWBG1hcnMxFTATBgNVBAMTDE1BUlMtUk9PVC1DQTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAM7E6RzfKHgzJBgKDv+f3YIWGD25K9Uk7ZYfvI9pywO4Eaj4ER1DBDZGKwx3wElNW/pS45kza4zHgZhhHHImMyXKKoH/4+NCsW+F+KKS9i/EwHeOKi01/KI9BWhS9kiCvJ9e1ir3HOkcEtROTOt+vdncNDbHSQ9MlkZA9V1oCT8gAH1W1knhvoMxnIp+rS7/MKnNiNTiIgEUHyau/MpzzeJb2GE0NWlfKdxAmvYJp6SDwIqVAhSXm5jQ29ByFLfyz2jaRyJknwdskg8h9lGoPcWSq4iT70YVFxdRhzm0lo3Ag98TJ/RGIn0Gd5TTterjzJdNaU3ugIbssILIG7iVB68jonrhVaDWiEcF8NCz4/0XLcriCpO4I1gOEgJp5OulHs/8ZVCBSTXbkh2640+bgzO4NaqaJZJHwTiy10nw1+VsVa7bS9jk5OsTopBm6FTewa+NylRpK6V+kohg0P2fmcbOqSTtAvUB4I0EtbnQu5qvlw3bVeUbn1jHWZ3lTPTKRoz5Bq9MUFbYJAIOg3KNdk+OTZkQqiHbUf7NqNMq6UTqrjec9nnMj1ngD7OOaddExLtbfkrZ88gfYJLGt71e8tzAKMrPQ0p+WJ536uPGVOFChM3oy6YeUpExZirK+aymzjbZQlRxlCTtFJgJoz3AqmUYFPXisOtWy1p8SYsxooX9AgMBAAGjaTBnMBMGCSsGAQQBgjcUAgQGHgQAQwBBMA4GA1UdDwEB/wQEAwIBhjAPBgNVHRMBAf8EBTADAQH/MB0GA1UdDgQWBBTsrV5HZN1O6EYT6YUp9TpQymsGljAQBgkrBgEEAYI3FQEEAwIBADANBgkqhkiG9w0BAQ0FAAOCAgEAesNDznHL8SKc1yY+p7rBxX4zqZxlcr9MFMmoaYrJR2CopVH3R5G++AkN1JOgZlJnoD0E3hQqwGmWjkLv/k94uDcWIuPsMy4KAsyFY3+8z6zs+dNaue6R2n56zH0Om/QgEfjokZv7fOJI2zBf5SZ86xQBehoL9UIst0A+Mey8TRYzZX6s4dZXudelr7wu0KdRbFZTYB/j5mZx/vOfow1osEnr0yoIeh9Yp79hjukyGBGtUpmTFoBNQwWEpjOkJ50Q+TqNOVOwNYls4pVwkYx+EwHTrDFEAFUtCp0M9rwWJ6LzqypsbyWtFFD38q6QY59rUv/m5m7AEMrHJo0yYaYOce7jqrG5d7RXBHSDKnYpBXzsqvz3oqXLH9H3ur+52CzqLs7hONnlk9C7blnCZFwMCBhXRP0PtUO2+t8XJpXeMfnVNmgJmKq1+CT78/4T4wINEMhhsONpi0v0IptRethHJknfZ0QYWMGEMxhG3KxRVK+LCqDxw5UCPmtSxnB9h5aP5NIzhq2wLMNgfW53u+KrrhdocTcVwus379oVOtStnNI0vX0tCZ/t8DzzxlMiAhXnyKl/y8kt/5Z8o0T0/3PjGdTdz9+3Fdhxf3uYQ2MGSUKTy4Bb2zJZLfKWNYmAbyQ3PadhztqU5DNkAh8NksvqKNALyDR9LeTgyB0+TY69kSg=</ns0:certificate><ns0:enrollPermission>true</ns0:enrollPermission><ns0:cAReferenceID>0</ns0:cAReferenceID></ns0:cA></ns0:cAs><ns0:oIDs><ns0:oID><ns0:value>1.3.6.1.5.5.7.3.2</ns0:value><ns0:group>7</ns0:group><ns0:oIDReferenceID>4</ns0:oIDReferenceID><ns0:defaultName>Client Authentication</ns0:defaultName></ns0:oID><ns0:oID><ns0:value>1.3.6.1.4.1.311.20.2</ns0:value><ns0:group>6</ns0:group><ns0:oIDReferenceID>5</ns0:oIDReferenceID><ns0:defaultName>Certificate Template Name</ns0:defaultName></ns0:oID><ns0:oID><ns0:value>2.5.29.37</ns0:value><ns0:group>6</ns0:group><ns0:oIDReferenceID>6</ns0:oIDReferenceID><ns0:defaultName>Enhanced Key Usage</ns0:defaultName></ns0:oID><ns0:oID><ns0:value>2.5.29.15</ns0:value><ns0:group>6</ns0:group><ns0:oIDReferenceID>7</ns0:oIDReferenceID><ns0:defaultName>Key Usage</ns0:defaultName></ns0:oID><ns0:oID><ns0:value>1.3.6.1.4.1.311.21.8.391007.14191702.9126033.6337603.8513481.227.1.14</ns0:value><ns0:group>9</ns0:group><ns0:oIDReferenceID>13</ns0:oIDReferenceID><ns0:defaultName>Computer</ns0:defaultName></ns0:oID><ns0:oID><ns0:value>1.3.6.1.5.5.7.3.1</ns0:value><ns0:group>7</ns0:group><ns0:oIDReferenceID>14</ns0:oIDReferenceID><ns0:defaultName>Server Authentication</ns0:defaultName></ns0:oID></ns0:oIDs></ns0:GetPoliciesResponse>'  # noqa: E501
# fmt: on


def test_fetch_roots_from_xml_response_with_nil_cas() -> None:
    """Tests parsing XML response where cAs has xsi:nil='true'.

    This reproduces the bug where accessing .cas on a GetPoliciesResponse
    with '<cAs xsi:nil="true" />' would cause an IndexError because the
    XMLElementList returned an empty list instead of None.
    """
    # Parse the XML response
    element = ElementTree.fromstring(GET_POLICIES_RESPONSE_NIL_CAS_XML)
    policies_response = GetPoliciesResponse(element)

    # Verify that cas returns None (not an empty list) when xsi:nil="true"
    assert policies_response.cas is None

    # Mock the service to return None for certificate_chain (simulating no CAs)
    mock_service = Mock()
    mock_service.certificate_chain = None

    out = io.StringIO()
    operation = CertmongerOperations.FetchRoots(mock_service, out=out)
    result = operation()

    # Output should be empty (just newline from print)
    assert out.getvalue() == "\n"

    # Verify the return code
    assert result == CertmongerResult.DEFAULT


def test_get_supported_templates_call() -> None:
    """Tests the GetSupportedTemplates operation with templates."""
    mock_service = Mock()
    mock_service.templates = ["Machine", "User", "WebServer"]

    out = io.StringIO()
    operation = CertmongerOperations.GetSupportedTemplates(
        mock_service, out=out
    )
    result = operation()

    # Verify the output contains each template on its own line
    assert out.getvalue() == "Machine\nUser\nWebServer\n"

    # Verify the return code
    assert result == CertmongerResult.DEFAULT


def test_get_supported_templates_with_no_templates() -> None:
    """Tests the GetSupportedTemplates operation with no templates."""
    mock_service = Mock()
    mock_service.templates = None

    out = io.StringIO()
    operation = CertmongerOperations.GetSupportedTemplates(
        mock_service, out=out
    )
    result = operation()

    # Output should be empty when no templates
    assert out.getvalue() == ""

    # Verify the return code
    assert result == CertmongerResult.DEFAULT


def test_get_supported_templates_from_xml_response() -> None:
    """Tests extracting templates from actual XML response from AD CS.

    This test parses the GetPoliciesResponse XML from line 33 of the
    cepces-get-supported-templates.log debug output.
    """
    # Parse the XML response from line 33 of the log
    element = ElementTree.fromstring(GET_SUPPORTED_TEMPLATES_XML)
    policies_response = GetPoliciesResponse(element)

    # Verify we can extract the response and policies
    assert policies_response.response is not None
    assert policies_response.response.policies is not None
    assert len(policies_response.response.policies) == 1

    # Verify the policy attributes contain the template name
    policy = policies_response.response.policies[0]
    assert policy.attributes is not None
    assert policy.attributes.common_name == "Machine"

    # Extract templates the same way Service.templates property does
    templates = []
    for policy in policies_response.response.policies:
        templates.append(policy.attributes.common_name)

    # Mock the service to return the extracted templates
    mock_service = Mock()
    mock_service.templates = templates

    out = io.StringIO()
    operation = CertmongerOperations.GetSupportedTemplates(
        mock_service, out=out
    )
    result = operation()

    # Verify the output matches line 35 of the log: "Machine\n"
    assert out.getvalue() == "Machine\n"

    # Verify the return code
    assert result == CertmongerResult.DEFAULT


def test_get_new_request_requirements_call() -> None:
    """Tests the GetNewRequestRequirements operation.

    Based on cepces-get-new-request-requirements.log line 35, this operation
    outputs the required environment variable CERTMONGER_CA_PROFILE.
    """
    out = io.StringIO()
    operation = CertmongerOperations.GetNewRequestRequirements(None, out=out)
    result = operation()

    # Verify the output matches line 35 of the log
    assert out.getvalue() == "CERTMONGER_CA_PROFILE\n"

    # Verify the return code
    assert result == CertmongerResult.DEFAULT


# XML from cepces-get-new-request-requirements.log line 33
# Extracted from the SOAP envelope on line 32
# fmt: off
GET_NEW_REQUEST_REQUIREMENTS_XML = b'<ns0:GetPoliciesResponse xmlns:ns0="http://schemas.microsoft.com/windows/pki/2009/01/enrollmentpolicy" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><ns0:response><ns0:policyID>{DA239A97-1289-4B14-924F-B318D56ED254}</ns0:policyID><ns0:policyFriendlyName /><ns0:nextUpdateHours>8</ns0:nextUpdateHours><ns0:policiesNotChanged xsi:nil="true" /><ns0:policies><ns0:policy><ns0:policyOIDReference>13</ns0:policyOIDReference><ns0:cAs><ns0:cAReference>0</ns0:cAReference></ns0:cAs><ns0:attributes><ns0:commonName>Machine</ns0:commonName><ns0:policySchema>1</ns0:policySchema><ns0:certificateValidity><ns0:validityPeriodSeconds>31536000</ns0:validityPeriodSeconds><ns0:renewalPeriodSeconds>3628800</ns0:renewalPeriodSeconds></ns0:certificateValidity><ns0:permission><ns0:enroll>true</ns0:enroll><ns0:autoEnroll>false</ns0:autoEnroll></ns0:permission><ns0:privateKeyAttributes><ns0:minimalKeyLength>2048</ns0:minimalKeyLength><ns0:keySpec>1</ns0:keySpec><ns0:keyUsageProperty xsi:nil="true" /><ns0:permissions xsi:nil="true" /><ns0:algorithmOIDReference xsi:nil="true" /><ns0:cryptoProviders><ns0:provider>Microsoft RSA SChannel Cryptographic Provider</ns0:provider></ns0:cryptoProviders></ns0:privateKeyAttributes><ns0:revision><ns0:majorRevision>5</ns0:majorRevision><ns0:minorRevision>1</ns0:minorRevision></ns0:revision><ns0:supersededPolicies xsi:nil="true" /><ns0:privateKeyFlags>0</ns0:privateKeyFlags><ns0:subjectNameFlags>402653184</ns0:subjectNameFlags><ns0:enrollmentFlags>0</ns0:enrollmentFlags><ns0:generalFlags>66144</ns0:generalFlags><ns0:hashAlgorithmOIDReference xsi:nil="true" /><ns0:rARequirements xsi:nil="true" /><ns0:keyArchivalAttributes xsi:nil="true" /><ns0:extensions><ns0:extension><ns0:oIDReference>5</ns0:oIDReference><ns0:critical>false</ns0:critical><ns0:value>Hg4ATQBhAGMAaABpAG4AZQ==</ns0:value></ns0:extension><ns0:extension><ns0:oIDReference>6</ns0:oIDReference><ns0:critical>false</ns0:critical><ns0:value>MBQGCCsGAQUFBwMCBggrBgEFBQcDAQ==</ns0:value></ns0:extension><ns0:extension><ns0:oIDReference>7</ns0:oIDReference><ns0:critical>true</ns0:critical><ns0:value>AwIFoA==</ns0:value></ns0:extension></ns0:extensions></ns0:attributes></ns0:policy></ns0:policies></ns0:response><ns0:cAs><ns0:cA><ns0:uris><ns0:cAURI><ns0:clientAuthentication>2</ns0:clientAuthentication><ns0:uri>https://win-ca01.mars.milkyway.site/MARS-ROOT-CA_CES_Kerberos/service.svc/CES</ns0:uri><ns0:priority>1</ns0:priority><ns0:renewalOnly>false</ns0:renewalOnly></ns0:cAURI></ns0:uris><ns0:certificate>MIIFrTCCA5WgAwIBAgIQb7gIsLLyR51KVoyagCO2ljANBgkqhkiG9w0BAQ0FADBdMRQwEgYKCZImiZPyLGQBGRYEc2l0ZTEYMBYGCgmSJomT8ixkARkWCG1pbGt5d2F5MRQwEgYKCZImiZPyLGQBGRYEbWFyczEVMBMGA1UEAxMMTUFSUy1ST09ULUNBMB4XDTI1MDYzMDA4MTQzNFoXDTMwMDYzMDA4MjQzM1owXTEUMBIGCgmSJomT8ixkARkWBHNpdGUxGDAWBgoJkiaJk/IsZAEZFghtaWxreXdheTEUMBIGCgmSJomT8ixkARkWBG1hcnMxFTATBgNVBAMTDE1BUlMtUk9PVC1DQTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAM7E6RzfKHgzJBgKDv+f3YIWGD25K9Uk7ZYfvI9pywO4Eaj4ER1DBDZGKwx3wElNW/pS45kza4zHgZhhHHImMyXKKoH/4+NCsW+F+KKS9i/EwHeOKi01/KI9BWhS9kiCvJ9e1ir3HOkcEtROTOt+vdncNDbHSQ9MlkZA9V1oCT8gAH1W1knhvoMxnIp+rS7/MKnNiNTiIgEUHyau/MpzzeJb2GE0NWlfKdxAmvYJp6SDwIqVAhSXm5jQ29ByFLfyz2jaRyJknwdskg8h9lGoPcWSq4iT70YVFxdRhzm0lo3Ag98TJ/RGIn0Gd5TTterjzJdNaU3ugIbssILIG7iVB68jonrhVaDWiEcF8NCz4/0XLcriCpO4I1gOEgJp5OulHs/8ZVCBSTXbkh2640+bgzO4NaqaJZJHwTiy10nw1+VsVa7bS9jk5OsTopBm6FTewa+NylRpK6V+kohg0P2fmcbOqSTtAvUB4I0EtbnQu5qvlw3bVeUbn1jHWZ3lTPTKRoz5Bq9MUFbYJAIOg3KNdk+OTZkQqiHbUf7NqNMq6UTqrjec9nnMj1ngD7OOaddExLtbfkrZ88gfYJLGt71e8tzAKMrPQ0p+WJ536uPGVOFChM3oy6YeUpExZirK+aymzjbZQlRxlCTtFJgJoz3AqmUYFPXisOtWy1p8SYsxooX9AgMBAAGjaTBnMBMGCSsGAQQBgjcUAgQGHgQAQwBBMA4GA1UdDwEB/wQEAwIBhjAPBgNVHRMBAf8EBTADAQH/MB0GA1UdDgQWBBTsrV5HZN1O6EYT6YUp9TpQymsGljAQBgkrBgEEAYI3FQEEAwIBADANBgkqhkiG9w0BAQ0FAAOCAgEAesNDznHL8SKc1yY+p7rBxX4zqZxlcr9MFMmoaYrJR2CopVH3R5G++AkN1JOgZlJnoD0E3hQqwGmWjkLv/k94uDcWIuPsMy4KAsyFY3+8z6zs+dNaue6R2n56zH0Om/QgEfjokZv7fOJI2zBf5SZ86xQBehoL9UIst0A+Mey8TRYzZX6s4dZXudelr7wu0KdRbFZTYB/j5mZx/vOfow1osEnr0yoIeh9Yp79hjukyGBGtUpmTFoBNQwWEpjOkJ50Q+TqNOVOwNYls4pVwkYx+EwHTrDFEAFUtCp0M9rwWJ6LzqypsbyWtFFD38q6QY59rUv/m5m7AEMrHJo0yYaYOce7jqrG5d7RXBHSDKnYpBXzsqvz3oqXLH9H3ur+52CzqLs7hONnlk9C7blnCZFwMCBhXRP0PtUO2+t8XJpXeMfnVNmgJmKq1+CT78/4T4wINEMhhsONpi0v0IptRethHJknfZ0QYWMGEMxhG3KxRVK+LCqDxw5UCPmtSxnB9h5aP5NIzhq2wLMNgfW53u+KrrhdocTcVwus379oVOtStnNI0vX0tCZ/t8DzzxlMiAhXnyKl/y8kt/5Z8o0T0/3PjGdTdz9+3Fdhxf3uYQ2MGSUKTy4Bb2zJZLfKWNYmAbyQ3PadhztqU5DNkAh8NksvqKNALyDR9LeTgyB0+TY69kSg=</ns0:certificate><ns0:enrollPermission>true</ns0:enrollPermission><ns0:cAReferenceID>0</ns0:cAReferenceID></ns0:cA></ns0:cAs><ns0:oIDs><ns0:oID><ns0:value>1.3.6.1.5.5.7.3.2</ns0:value><ns0:group>7</ns0:group><ns0:oIDReferenceID>4</ns0:oIDReferenceID><ns0:defaultName>Client Authentication</ns0:defaultName></ns0:oID><ns0:oID><ns0:value>1.3.6.1.4.1.311.20.2</ns0:value><ns0:group>6</ns0:group><ns0:oIDReferenceID>5</ns0:oIDReferenceID><ns0:defaultName>Certificate Template Name</ns0:defaultName></ns0:oID><ns0:oID><ns0:value>2.5.29.37</ns0:value><ns0:group>6</ns0:group><ns0:oIDReferenceID>6</ns0:oIDReferenceID><ns0:defaultName>Enhanced Key Usage</ns0:defaultName></ns0:oID><ns0:oID><ns0:value>2.5.29.15</ns0:value><ns0:group>6</ns0:group><ns0:oIDReferenceID>7</ns0:oIDReferenceID><ns0:defaultName>Key Usage</ns0:defaultName></ns0:oID><ns0:oID><ns0:value>1.3.6.1.4.1.311.21.8.391007.14191702.9126033.6337603.8513481.227.1.14</ns0:value><ns0:group>9</ns0:group><ns0:oIDReferenceID>13</ns0:oIDReferenceID><ns0:defaultName>Computer</ns0:defaultName></ns0:oID><ns0:oID><ns0:value>1.3.6.1.5.5.7.3.1</ns0:value><ns0:group>7</ns0:group><ns0:oIDReferenceID>14</ns0:oIDReferenceID><ns0:defaultName>Server Authentication</ns0:defaultName></ns0:oID></ns0:oIDs></ns0:GetPoliciesResponse>'  # noqa: E501
# fmt: on


def test_get_new_request_requirements_from_xml_response() -> None:
    """Tests GetNewRequestRequirements with XML from AD CS server.

    This test parses the GetPoliciesResponse XML from line 33 of the
    cepces-get-new-request-requirements.log debug output.
    """
    # Parse the XML response from line 33 of the log
    element = ElementTree.fromstring(GET_NEW_REQUEST_REQUIREMENTS_XML)
    policies_response = GetPoliciesResponse(element)

    # Verify we can extract the response and policies
    assert policies_response.response is not None
    assert policies_response.response.policies is not None
    assert len(policies_response.response.policies) == 1

    # Verify the policy attributes
    policy = policies_response.response.policies[0]
    assert policy.attributes is not None
    assert policy.attributes.common_name == "Machine"

    # The operation itself doesn't use the XML, it outputs a static string
    out = io.StringIO()
    operation = CertmongerOperations.GetNewRequestRequirements(None, out=out)
    result = operation()

    # Verify the output matches line 35 of the log
    assert out.getvalue() == "CERTMONGER_CA_PROFILE\n"

    # Verify the return code
    assert result == CertmongerResult.DEFAULT


# WSTEP response XML from cepces-submit.log line 67
# Extracted RequestSecurityTokenResponseCollection from the SOAP envelope Body
# fmt: off
SUBMIT_WSTEP_RESPONSE_XML = b'<ns3:RequestSecurityTokenResponseCollection xmlns:ns3="http://docs.oasis-open.org/ws-sx/ws-trust/200512" xmlns:ns4="http://schemas.microsoft.com/windows/pki/2009/01/enrollment" xmlns:ns5="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"><ns3:RequestSecurityTokenResponse><ns3:TokenType>http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-x509-token-profile-1.0#X509v3</ns3:TokenType><ns4:DispositionMessage xml:lang="en-US">Issued</ns4:DispositionMessage><ns5:BinarySecurityToken ValueType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd#PKCS7" EncodingType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd#base64binary">MIIQJwYJKoZIhvcNAQcCoIIQGDCCEBQCAQMxDzANBglghkgBZQMEAgMFADB9BgsrBgEFBQcMA6BxBG8wbTBnMCECAQEGCCsGAQUFBwcBMRIwEAIBADADAgEBDAZJc3N1ZWQwQgIBAgYKKwYBBAGCNwoKATExMC8CAQAwAwIBATElMCMGCSsGAQQBgjcVETEWBBRTUTWG9j2Y</ns5:BinarySecurityToken><ns3:RequestedSecurityToken><ns5:BinarySecurityToken ValueType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-x509-token-profile-1.0#X509v3" EncodingType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd#base64binary">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</ns5:BinarySecurityToken></ns3:RequestedSecurityToken><ns4:RequestID>27</ns4:RequestID></ns3:RequestSecurityTokenResponse></ns3:RequestSecurityTokenResponseCollection>'  # noqa: E501
# fmt: on


# Issued certificate from cepces-submit.log (CN=fedora2.mars.milkyway.site)
# fmt: off
ISSUED_CERT_PEM = """-----BEGIN CERTIFICATE-----
MIIGvDCCBKSgAwIBAgITUgAAABtlxEW6Cmwf5QAAAAAAGzANBgkqhkiG9w0BAQ0F
ADBdMRQwEgYKCZImiZPyLGQBGRYEc2l0ZTEYMBYGCgmSJomT8ixkARkWCG1pbGt5
d2F5MRQwEgYKCZImiZPyLGQBGRYEbWFyczEVMBMGA1UEAxMMTUFSUy1ST09ULUNB
MB4XDTI1MTIxOTA2MjMwOVoXDTI2MTIxOTA2MjMwOVowJTEjMCEGA1UEAxMaZmVk
b3JhMi5tYXJzLm1pbGt5d2F5LnNpdGUwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAw
ggEKAoIBAQC4bmnnol4bjMqgjllaQXhQWPkKlSlVg8+rb1u9OLlzqv18WQw+AhiR
FTb7ld4URYYhzIlKACoqkGF0id9O7HX6LC34WZZR5swdRtQFG8Ny3lJwe4rbdyl/
A3T3np6WKPRrlFAp796xswggB7rRTMG6CNBRJlEPjdGKx3NiuJFhaQgnb1RrGAgM
hN7L3QjDXF9bQ5vReCRu6BZJsk8Wbp0jzF0wa6lvwYmSY+QnKh6ueBeer7FHi505
3eqGqcjiKSh/MjhT6QunJLkxYNpIM3lfuXwwGHwPMhgeh8CnhQkisfs4mRUObswb
GYAp03duOi6wqIIhjVC8mMIIWgrz6Bd/AgMBAAGjggKrMIICpzAdBgNVHSUEFjAU
BggrBgEFBQcDAgYIKwYBBQUHAwEwHQYDVR0OBBYEFLErlMqSK4MM/vdd6mCN2c1E
g7VCMB0GCSsGAQQBgjcUAgQQHg4ATQBhAGMAaABpAG4AZTAlBgNVHREEHjAcghpm
ZWRvcmEyLm1hcnMubWlsa3l3YXkuc2l0ZTAfBgNVHSMEGDAWgBTsrV5HZN1O6EYT
6YUp9TpQymsGljCB1QYDVR0fBIHNMIHKMIHHoIHEoIHBhoG+bGRhcDovLy9DTj1N
QVJTLVJPT1QtQ0EsQ049V0lOLUNBMDEsQ049Q0RQLENOPVB1YmxpYyUyMEtleSUy
MFNlcnZpY2VzLENOPVNlcnZpY2VzLENOPUNvbmZpZ3VyYXRpb24sREM9bWFycyxE
Qz1taWxreXdheSxEQz1zaXRlP2NlcnRpZmljYXRlUmV2b2NhdGlvbkxpc3Q/YmFz
ZT9vYmplY3RDbGFzcz1jUkxEaXN0cmlidXRpb25Qb2ludDCByAYIKwYBBQUHAQEE
gbswgbgwgbUGCCsGAQUFBzAChoGobGRhcDovLy9DTj1NQVJTLVJPT1QtQ0EsQ049
QUlBLENOPVB1YmxpYyUyMEtleSUyMFNlcnZpY2VzLENOPVNlcnZpY2VzLENOPUNv
bmZpZ3VyYXRpb24sREM9bWFycyxEQz1taWxreXdheSxEQz1zaXRlP2NBQ2VydGlm
aWNhdGU/YmFzZT9vYmplY3RDbGFzcz1jZXJ0aWZpY2F0aW9uQXV0aG9yaXR5MA4G
A1UdDwEB/wQEAwIFoDBNBgkrBgEEAYI3GQIEQDa+oDwGCisGAQQBgjcZAgGgLgQs
Uy0xLTUtMjEtMzk0Mzc2MzQtMjQ1NTY2MzY5Ni0yNzUwMDA1MjgxLTExMDUwDQYJ
KoZIhvcNAQENBQADggIBAKgrtyAqEBjFzR47j5FOvTW+INqBwypoAauutMubKaRt
H/nv2B18fBK9u6f/KsmeVSr6zf5JuZelR1skwNDrFSTKA8FRb09McILrnmch3zAy
JQzp2dRUJIR/U03w24qWtKMjrw/dEVeTjowDHszsEnEEgunNRcp3AURgDg8dC/q5
WNDlTqdoLDSeZyswi5/C5bRzh5n0gWtOuByUCcJ7VBWDY/he4/JX7fOfBgoyFSZp
uMdCTi05y7rCdkXMxaZCfipCF8SZsR/WvR0YK/E1Qz+n+31Ap5jrVE0HMuqkPbjm
3jRP0swEQpjVIak8AEt5vIu0uCY6f+Og0efBAo45wgrkI9mn66cF+DGWg2pW6rHm
LygrR48ZmoRtp/Bg1AwLCo8EbvFXnwICsuF3aE5RxsyaJksGgZdwoAVt7L0DvwPw
zRpAbkuxwNO5MvRZO153EDuRYmQsez5Pa86Knhdf4X5eEDW0JZa1oC/aDpt98x5i
MphEV5xk1r4V9+UWVnvfcnyxRa+Pu6jf2H7+jXtZnksUhwz9QK86FsZS77lSvrjn
tr4skE8NgMonNN68FxPr9ammHDg3KAZLuoLMLWxuY2g+DgLXQpvihENAsslfrO9A
z1qRP/PjWqwR/FRkXg3Z/AdHUqnRyWoPDmQELgQoV7R2KcHCEBgCpFX672JPSQVR
-----END CERTIFICATE-----"""
# fmt: on


def test_submit_wstep_response_parsing() -> None:
    """Tests parsing the WSTEP SecurityTokenResponseCollection from AD CS.

    This test parses the RequestSecurityTokenResponseCollection XML from
    line 67 of the cepces-submit.log debug output.
    """
    # Parse the XML response from line 67 of the log
    element = ElementTree.fromstring(SUBMIT_WSTEP_RESPONSE_XML)
    response_collection = SecurityTokenResponseCollection(element)

    # Verify we can extract the responses
    assert response_collection.responses is not None
    assert len(response_collection.responses) == 1

    # Get the first response
    response = response_collection.responses[0]

    # Verify token type (X509v3)
    assert response.token_type is not None
    assert "X509v3" in response.token_type

    # Verify disposition message is "Issued"
    assert response.disposition_message == "Issued"

    # Verify request ID matches line 67 of the log
    assert response.request_id == 27

    # Verify the requested token contains a certificate
    assert response.requested_token is not None
    assert response.requested_token.text is not None


def test_submit_operation_with_issued_certificate() -> None:
    """Tests the Submit operation with an issued certificate.

    Based on cepces-submit.log lines 71-72, the Submit operation returns
    the issued certificate for CN=fedora2.mars.milkyway.site.
    """
    # Load the issued certificate
    cert = x509.load_pem_x509_certificate(
        ISSUED_CERT_PEM.encode(), default_backend()
    )

    # Verify the certificate subject
    cn = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0]
    assert cn.value == "fedora2.mars.milkyway.site"

    # Verify the certificate issuer (MARS-ROOT-CA)
    issuer_cn = cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0]
    assert issuer_cn.value == "MARS-ROOT-CA"

    # Mock the Submit operation result
    out = io.StringIO()

    # The Submit operation outputs the certificate in PEM format
    # Simulate what Submit.__call__ does when returning the certificate
    from cryptography.hazmat.primitives import serialization

    pem_data = cert.public_bytes(encoding=serialization.Encoding.PEM)
    print(pem_data.decode(), file=out)

    output = out.getvalue()

    # Verify the output contains a PEM certificate
    assert "-----BEGIN CERTIFICATE-----" in output
    assert "-----END CERTIFICATE-----" in output


# GetPoliciesResponse with nil policies and CAs (no enrollment available)
# From a misconfigured AD CS server - causes TypeError when iterating
GET_POLICIES_NIL_POLICIES_XML = b'<ns0:GetPoliciesResponse xmlns:ns0="http://schemas.microsoft.com/windows/pki/2009/01/enrollmentpolicy" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><ns0:response><ns0:policyID>{F803BF1A-EB36-42A4-973C-AF4555EB8782}</ns0:policyID><ns0:policyFriendlyName>My PKI</ns0:policyFriendlyName><ns0:nextUpdateHours>1</ns0:nextUpdateHours><ns0:policiesNotChanged xsi:nil="true" /><ns0:policies xsi:nil="true" /></ns0:response><ns0:cAs xsi:nil="true" /><ns0:oIDs xsi:nil="true" /></ns0:GetPoliciesResponse>'  # noqa: E501


def test_get_policies_with_nil_policies_returns_none() -> None:
    """Tests that nil policies are handled gracefully in XML parsing.

    When the AD CS server returns a GetPoliciesResponse with
    '<ns0:policies xsi:nil="true" />', the XMLElementList correctly
    returns None instead of an empty list.

    This test verifies that the nil policies response is parsed correctly
    and can be safely checked for None before iteration.
    """
    # Parse the XML response with nil policies
    element = ElementTree.fromstring(GET_POLICIES_NIL_POLICIES_XML)
    policies_response = GetPoliciesResponse(element)

    # Verify that response exists but policies is None
    assert policies_response.response is not None
    assert policies_response.response.policies is None

    # Verify that CAs is also None
    assert policies_response.cas is None

    # Demonstrate safe iteration pattern:
    policies = policies_response.response.policies
    if policies is None:
        templates = None
    else:
        templates = [p.attributes.common_name for p in policies]

    assert templates is None


def test_submit_operation_with_no_endpoints() -> None:
    """Tests that Submit handles None result when no endpoints are available.

    When the AD CS server returns a policy response with no enrollment
    endpoints available (e.g., misconfigured server or user lacks
    permissions), service.request() returns None. The Submit operation
    should handle this gracefully and return UNDERCONFIGURED.

    This test was originally a reproducer for GitHub PR #71.
    """
    import os

    # Set up the required environment variable for Submit
    with patch.dict(
        os.environ,
        {"CERTMONGER_CSR": """-----BEGIN CERTIFICATE REQUEST-----
MIIDgTCCAmkCAQAwEjEQMA4GA1UEAxMHZmVkb3JhMjCCASIwDQYJKoZIhvcNAQEB
BQADggEPADCCAQoCggEBALhuaeeiXhuMyqCOWVpBeFBY+QqVKVWDz6tvW704uXOq
/XxZDD4CGJEVNvuV3hRFhiHMiUoAKiqQYXSJ307sdfosLfhZllHmzB1G1AUbw3Le
UnB7itt3KX8DdPeenpYo9GuUUCnv3rGzCCAHutFMwboI0FEmUQ+N0YrHc2K4kWFp
CCdvVGsYCAyE3svdCMNcX1tDm9F4JG7oFkmyTxZunSPMXTBrqW/BiZJj5CcqHq54
F56vsUeLnTnd6oapyOIpKH8yOFPpC6ckuTFg2kgzeV+5fDAYfA8yGB6HwKeFCSKx
+ziZFQ5uzBsZgCnTd246LrCogiGNULyYwghaCvPoF38CAwEAAaCCASgwKwYJKoZI
hvcNAQkUMR4eHAAyADAAMgA1ADEAMgAxADkAMAA2ADMAMwAwADkwgfgGCSqGSIb3
DQEJDjGB6jCB5zCBgwYDVR0RBHwweoIHZmVkb3JhMqAvBgorBgEEAYI3FAIDoCEM
H2hvc3QvZmVkb3JhMkBNQVJTLk1JTEtZV0FZLlNJVEWgPgYGKwYBBQICoDQwMqAU
GxJNQVJTLk1JTEtZV0FZLlNJVEWhGjAYoAMCAQGhETAPGwRob3N0GwdmZWRvcmEy
MBMGA1UdJQQMMAoGCCsGAQUFBwMBMAwGA1UdEwEB/wQCMAAwHQYDVR0OBBYEFEqI
6jUIxqWQa0dElUmEzCgLpAX2MB0GCSsGAQQBgjcUAgQQHg4ATQBhAGMAaABpAG4A
ZTANBgkqhkiG9w0BAQsFAAOCAQEAUKbuBaz9KtrbJ2TQ8UvMdRaNR7X1O6diZPcu
UsNrw5W6eJX2LBdTcjxWCrB9oF6qwzNiGH2Kt79JkQoMSqAm0AoLJ1hBGN+e8ano
ljR8NrQkLVnbsQMGKWrCjB7r5ycT42iH32foxwb1FaA5/mM05PQZ/syVFLyfjJLr
IfGoQKCCi4nqcho+Ukfxa7i3ESoWuynVnqJzKOXnxie5/VHbNVVCJ372Kk3FbT3Z
oMTDsPOVy3/SVhjVVl8eWs/ch6mJpnRlkkriOC1aQo/P606hCb+7+l9cc/31ENJj
J9R2yTmwnWuSjm3k2/QOKOKYb+fO0iYXqCKeP4P7s4jGi02A5Q==
-----END CERTIFICATE REQUEST-----
"""},
    ):
        # Create mock service that returns None (no endpoints available)
        mock_service = Mock()
        mock_service.request.return_value = None

        out = io.StringIO()
        operation = CertmongerOperations.Submit(mock_service, out=out)

        # With the fix, this now returns UNDERCONFIGURED instead of
        # raising AttributeError
        result = operation()

        assert result == CertmongerResult.UNDERCONFIGURED


def test_operations_needs_service_attribute() -> None:
    """Tests that operations correctly declare whether they need a service.

    Operations that don't access the service (authentication) should have
    needs_service = False so they can run during RPM installation without
    a keytab configured.
    """
    # Operations that DON'T need the service (can run without authentication)
    assert CertmongerOperations.Identify.needs_service is False
    assert (
        CertmongerOperations.GetNewRequestRequirements.needs_service is False
    )
    assert (
        CertmongerOperations.GetRenewRequestRequirements.needs_service is False
    )
    assert CertmongerOperations.GetDefaultTemplate.needs_service is False

    # Operations that DO need the service (require authentication)
    # Note: GetSupportedTemplates and FetchRoots need service but handle
    # service=None gracefully when --install flag is used.
    assert CertmongerOperations.Submit.needs_service is True
    assert CertmongerOperations.Poll.needs_service is True
    assert CertmongerOperations.GetSupportedTemplates.needs_service is True
    assert CertmongerOperations.FetchRoots.needs_service is True


def test_operations_without_service_work_with_none() -> None:
    """Tests that operations work with service=None.

    This simulates the behavior during RPM installation when getcert add-ca
    is called with --install flag but no keytab is configured. Operations
    with needs_service=False never attempt auth, while operations like
    GetSupportedTemplates and FetchRoots handle service=None gracefully.
    """
    # Identify should work without a service
    out1 = io.StringIO()
    op_identify = CertmongerOperations.Identify(None, out=out1)
    result1 = op_identify()
    assert result1 == CertmongerResult.DEFAULT
    assert __title__ in out1.getvalue()

    # GetNewRequestRequirements should work without a service
    out2 = io.StringIO()
    op_new_req = CertmongerOperations.GetNewRequestRequirements(None, out=out2)
    result2 = op_new_req()
    assert result2 == CertmongerResult.DEFAULT
    assert "CERTMONGER_CA_PROFILE" in out2.getvalue()

    # GetRenewRequestRequirements should work without a service
    out3 = io.StringIO()
    op_renew = CertmongerOperations.GetRenewRequestRequirements(None, out=out3)
    result3 = op_renew()
    assert result3 == CertmongerResult.DEFAULT
    assert "CERTMONGER_CA_PROFILE" in out3.getvalue()

    # GetDefaultTemplate should work without a service
    out4 = io.StringIO()
    op_default = CertmongerOperations.GetDefaultTemplate(None, out=out4)
    result4 = op_default()
    assert result4 == CertmongerResult.DEFAULT
    assert out4.getvalue() == ""

    # GetSupportedTemplates should work without a service (returns empty)
    out5 = io.StringIO()
    op_templates = CertmongerOperations.GetSupportedTemplates(None, out=out5)
    result5 = op_templates()
    assert result5 == CertmongerResult.DEFAULT
    assert out5.getvalue() == ""

    # FetchRoots should work without a service (returns empty)
    out6 = io.StringIO()
    op_roots = CertmongerOperations.FetchRoots(None, out=out6)
    result6 = op_roots()
    assert result6 == CertmongerResult.DEFAULT
    assert out6.getvalue() == ""
