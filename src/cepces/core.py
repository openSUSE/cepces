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
# pylint: disable=invalid-name,no-self-use
"""Module containing core classes and functionality."""

from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import dsa
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import AuthorityInformationAccessOID
import requests
from cepces import Base
from cepces.config import Configuration
from cepces.http import create_session
from cepces.xcep.service import Service as XCEPService
from cepces.wstep.service import Service as WSTEPService


class PartialChainError(RuntimeError):
    """Error raised when a complete certificate chain cannot be retrieved."""

    def __init__(self, msg: str | Exception, result: list[x509.Certificate]):
        super().__init__(msg)
        self._result = result

    @property
    def result(self) -> list[x509.Certificate]:
        """Return the result so far."""
        return self._result


class Service(Base):
    """Main service."""

    class Endpoint(Base):
        """Internal class representing potential endpoints."""

        def __init__(
            self, url: str, priority: int, renewal_only: bool
        ) -> None:
            super().__init__()

            self._url = url
            self._priority = priority
            self._renewal_only = renewal_only

        @property
        def url(self) -> str:
            """Get the URL."""
            return self._url

        @property
        def priority(self) -> int:
            """Get the priority."""
            return self._priority

        @property
        def renewal_only(self) -> bool:
            """Can this endpoint be used only for renewals?"""
            return self._renewal_only

        def __str__(self) -> str:
            return self.url

    def __init__(self, config: Configuration) -> None:
        super().__init__()

        self._config = config
        self._session = create_session(config.openssl_ciphers)
        self._xcep: XCEPService | None

        if config.endpoint is None:
            raise RuntimeError("Configuration endpoint is required")

        if config.endpoint_type == "Policy":
            self._xcep = XCEPService(
                endpoint=config.endpoint,
                auth=config.auth,
                capath=config.cas,
                openssl_ciphers=config.openssl_ciphers,
            )

            # Eagerly load the policy response.
            self._policies = self._xcep.get_policies()
        elif config.endpoint_type == "Enrollment":
            self._xcep = None
            self._ces = WSTEPService(
                endpoint=config.endpoint,
                auth=config.auth,
                capath=config.cas,
                openssl_ciphers=config.openssl_ciphers,
            )

    @property
    def templates(self) -> list[str] | None:
        """Retrieve a list of available templates.

        Returns None if no policy endpoint is used or if no policies are
        available (e.g., when the server returns xsi:nil="true" for policies).
        """
        if self._xcep is None:
            return None

        policies = self._policies.response.policies
        if policies is None:
            return None

        templates: list[str] = []

        for policy in policies:
            templates.append(policy.attributes.common_name)

        return templates

    @property
    def endpoints(self) -> list["Service.Endpoint"] | None:
        """Retrieves a list of WSTEP suitable endpoints.

        Returns None if no policy endpoint is used or if no CAs are available
        (e.g., when the server returns xsi:nil="true" for cAs).
        """
        if self._xcep is None:
            return None

        cas = self._policies.cas
        if cas is None:
            return None

        config = self._config
        endpoints: list[Service.Endpoint] = []

        for ca in cas:
            for uri in [x for x in ca.uris if x.id in Configuration.AUTH_MAP]:
                if isinstance(config.auth, Configuration.AUTH_MAP[uri.id]):
                    endpoints.append(
                        Service.Endpoint(
                            uri.uri,
                            uri.priority,
                            uri.renewal_only,
                        ),
                    )

        return sorted(endpoints, key=lambda x: x.priority)

    @property
    def certificate_chain(
        self, index: int = 0
    ) -> list[x509.Certificate] | None:
        """Get the complete certification authority chain.

        This retrieves the certificate from the issuing endpoint service, and
        then uses the AIA information to retrieve the rest of the chain.

        This is only implemented for Policy endpoints. Returns None otherwise,
        or if no CAs are available (e.g., when the server returns
        xsi:nil="true" for cAs).

        :raise PartialChainError: if no AIA is found, or the complete chain
                                  cannot be retrieved. The exception contains
                                  the partial result.
        """
        if self._xcep is None:
            return None

        cas = self._policies.cas
        if cas is None:
            return None

        # Get the first certificate. Since is (or at least always should) be
        # securely retrieved over a secure channel, only verify subsequent
        # certificates.
        data = cas[index].certificate

        return list(reversed(self._resolve_chain(data)))

    def _request_ces(
        self, csr: x509.CertificateSigningRequest
    ) -> "WSTEPService.Response | None":
        """Request a certificate with a CSR from a CES endpoint."""
        csr_bytes = csr.public_bytes(serialization.Encoding.PEM)
        csr_raw = csr_bytes.decode("utf-8").strip()
        response = self._ces.request(csr_raw)

        # There should only be one response, as we only send one request.
        if response:
            # Convert to proper certificate, if possible.
            r = response[0]

            if r.token:
                pem = r.token.encode()
                cert = x509.load_pem_x509_certificate(pem, default_backend())
                r.token = cert

            return r
        return None

    def _request_cep(
        self, csr: x509.CertificateSigningRequest, renew: bool = False
    ) -> "WSTEPService.Response | None":
        """Request a certificate with a CSR through a CEP endpoint."""
        endpoint = None

        for candidate in self.endpoints or []:
            # If not renewing and the endpoint only supports renewal, ignore
            # it.
            if renew and candidate.renewal_only or not candidate.renewal_only:
                endpoint = candidate

                break

        # No endpoint found.
        if not endpoint:
            return None

        self._ces = WSTEPService(
            endpoint=str(endpoint),
            auth=self._config.auth,
            capath=self._config.cas,
            openssl_ciphers=self._config.openssl_ciphers,
        )

        return self._request_ces(csr)

    def request(
        self, csr: x509.CertificateSigningRequest, renew: bool = False
    ) -> "WSTEPService.Response | None":
        """Request a certificate with a CSR."""
        if self._xcep:
            return self._request_cep(csr, renew)
        else:
            return self._request_ces(csr)

    def poll(
        self, request_id: int, uri: str
    ) -> "WSTEPService.Response | None":
        """Poll the status of a previous request."""
        ces = WSTEPService(
            endpoint=uri,
            auth=self._config.auth,
            capath=self._config.cas,
            openssl_ciphers=self._config.openssl_ciphers,
        )

        response = ces.poll(request_id)

        # There should only be one response, as we only send one request.
        if response:
            # Convert to proper certificate, if possible.
            r = response[0]

            if r.token:
                pem = r.token.encode()
                cert = x509.load_pem_x509_certificate(pem, default_backend())
                r.token = cert

            return r
        return None

    def _verify_certificate_signature(
        self, cert: x509.Certificate, issuer: x509.Certificate
    ) -> bool:
        """Verify that the certificate is signed.

        :param cert: the certificate to verify
        :param issuer: the certificate's issuer certificate
        :raise InvalidSignature: if the signature cannot be verified
        :return: True on successful verification
        """
        sig_hash_alg = cert.signature_hash_algorithm
        sig_bytes = cert.signature
        sig_data = cert.tbs_certificate_bytes
        issuer_public_key = issuer.public_key()

        # signature_hash_algorithm is None for signatures without hash (e.g.
        # Ed25519), but we only support RSA and ECDSA which require a hash.
        assert sig_hash_alg is not None

        # Check the type of public key
        if isinstance(issuer_public_key, rsa.RSAPublicKey):
            issuer_public_key.verify(
                sig_bytes,
                sig_data,
                padding.PKCS1v15(),
                sig_hash_alg,
            )
        elif isinstance(issuer_public_key, ec.EllipticCurvePublicKey):
            issuer_public_key.verify(
                sig_bytes,
                sig_data,
                ec.ECDSA(sig_hash_alg),
            )
        elif isinstance(issuer_public_key, dsa.DSAPublicKey):
            issuer_public_key.verify(
                sig_bytes,
                sig_data,
                sig_hash_alg,
            )
        else:
            raise TypeError(
                f"Unsupported public key type: {type(issuer_public_key)}"
            )

        return True

    def _resolve_chain(
        self, data: str, child: x509.Certificate | None = None
    ) -> list[x509.Certificate]:
        """Recursive method for resolving a certificate. This starts with the
        data for a certificate, and a possible child certificate that needs to
        be validated. This is a reversed approach as the process is to start
        with a issued certificate and validate it upwards, until the root
        CA is reached.

        :param data: PEM encoded certificate to resolve.
        :param child: Optional child to validate.
        :raise PartialChainError: if no AIA is found, or the complete chain
                                  cannot be retrieved. The exception contains
                                  the partial result.
        """
        result: list[x509.Certificate] = []
        extension = x509.AuthorityInformationAccess
        oid = AuthorityInformationAccessOID

        # Load the certificate.
        try:
            cert = x509.load_pem_x509_certificate(
                data.encode(),
                default_backend(),
            )
        except ValueError:
            # The cert may be DER encoded instead
            cert = x509.load_der_x509_certificate(
                data.encode(),
                default_backend(),
            )

        # If no child is present, this is the first cert and thus cannot be
        # verified yet.
        # If there is a child, verify the signature.
        if not child:
            result.append(cert)
        elif self._verify_certificate_signature(child, cert):
            result.append(cert)
        else:
            raise PartialChainError(
                "Could not verify certificate chain "
                "({} not signed by {})".format(
                    child.subject,
                    cert.subject,
                ),
                result,
            )

        # If the issuer and subject are the same, this is a root certificate.
        # break here.
        if cert.subject == cert.issuer:
            return result

        try:
            # Get all AIA extensions from the certificate.
            aias = cert.extensions.get_extension_for_class(extension)

            for aia in aias.value:
                # Ignore anything but issuers.
                if aia.access_method == oid.CA_ISSUERS:
                    uri = aia.access_location.value

                    # Try to fetch the certificate.
                    r = self._session.get(uri)
                    r.raise_for_status()

                    parent = self._resolve_chain(r.text, cert)

                    if parent:
                        result.extend(parent)
        except x509.ExtensionNotFound as e:
            raise PartialChainError("Missing AIA", result) from e
        except requests.exceptions.RequestException as e:
            raise PartialChainError(e, result) from e
        except InvalidSignature as e:
            raise PartialChainError(e, result) from e

        return result
