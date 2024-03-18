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
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
import requests
from cepces import Base
from cepces.config import Configuration
from cepces.xcep.service import Service as XCEPService
from cepces.wstep.service import Service as WSTEPService


class PartialChainError(RuntimeError):
    """Error raised when a complete certificate chain cannot be retreived."""
    def __init__(self, msg, result):
        super().__init__(msg)
        self._result = result

    @property
    def result(self):
        """Return the result so far."""
        return self._result


class Service(Base):
    """Main service."""
    class Endpoint(Base):
        """Internal class representing potential endpoints."""
        def __init__(self, url, priority, renewal_only):
            super().__init__()

            self._url = url
            self._priority = priority
            self._renewal_only = renewal_only

        @property
        def url(self):
            """Get the URL."""
            return self._url

        @property
        def priority(self):
            """Get the priority."""
            return self._priority

        @property
        def renewal_only(self):
            """Can this endpoint be used only for renewals?"""
            return self._renewal_only

        def __str__(self):
            return self.url

    def __init__(self, config):
        super().__init__()

        self._config = config

        if config.endpoint_type == 'Policy':
            self._xcep = XCEPService(
                endpoint=config.endpoint,
                auth=config.auth,
                capath=config.cas,
            )

            # Eagerly load the policy response.
            self._policies = self._xcep.get_policies()
        elif config.endpoint_type == 'Enrollment':
            self._xcep = None
            self._ces = WSTEPService(
                endpoint=config.endpoint,
                auth=config.auth,
                capath=config.cas,
            )

    @property
    def templates(self):
        """Retrieve a list of available templates.

        Returns None if no policy endpoint is used.
        """
        if self._xcep is None:
            return None

        templates = []

        for policy in self._policies.response.policies:
            templates.append(policy.attributes.common_name)

        return templates

    @property
    def endpoints(self):
        """Retrieves a list of WSTEP suitable endpoints.

        Returns None if no policy endpoint is used.
        """
        if self._xcep is None:
            return None

        config = self._config
        endpoints = []

        for ca in self._policies.cas:
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
    def certificate_chain(self, index=0):
        """Get the complete certification authority chain.

        This retreives the certificate from the issuing endpoint service, and
        then uses the AIA information to retreive the rest of the chain.

        This is only implemented for Policy endpoints. Returns None otherwise.

        :raise PartialChainError: if no AIA is found, or the complete chain
                                  cannot be retreived. The exception contains
                                  the partial result.
        """
        if self._xcep is None:
            return None

        # Get the first certificate. Since is (or at least always should) be
        # securely retreived over a secure channel, only verify subsequent
        # certificates.
        data = self._policies.cas[index].certificate

        return reversed(self._resolve_chain(data))

    def _request_ces(self, csr):
        """Request a certificate with a CSR from a CES endpoint."""
        csr_bytes = csr.public_bytes(serialization.Encoding.PEM)
        csr_raw = csr_bytes.decode('utf-8').strip()
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

    def _request_cep(self, csr, renew=False):
        """Request a certificate with a CSR through a CEP endpoint."""
        endpoint = None

        for candidate in self.endpoints:
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
        )

        return self._request_ces(csr)

    def request(self, csr, renew=False):
        """Request a certificate with a CSR."""
        if self._xcep:
            return self._request_cep(csr, renew)
        else:
            return self._request_ces(csr)

    def poll(self, request_id, uri):
        """Poll the status of a previous request."""
        ces = WSTEPService(
            endpoint=uri,
            auth=self._config.auth,
            capath=self._config.cas,
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

    def _verify_certificate_signature(self, cert, issuer):
        """Verify that the certificate is signed.

        :param cert: the certificate to verify
        :param issuer: the certificate's issuer certificate
        :raise InvalidSignature: if the signature cannot be verified
        :return: True on successful verification
        """
        sig_hash_alg = cert.signature_hash_algorithm
        sig_bytes = cert.signature
        issuer_public_key = issuer.public_key()

        # Check the type of public key
        if isinstance(issuer_public_key, rsa.RSAPublicKey):
            verifier = issuer_public_key.verifier(
                sig_bytes, padding.PKCS1v15(), sig_hash_alg,
            )
        elif isinstance(issuer_public_key, ec.EllipticCurvePublicKey):
            verifier = issuer_public_key.verifier(
                sig_bytes, ec.ECDSA(sig_hash_alg),
            )
        else:
            verifier = issuer_public_key.verifier(
                sig_bytes, sig_hash_alg,
            )

        verifier.update(cert.tbs_certificate_bytes)
        verifier.verify()

        return True

    def _resolve_chain(self, data, child=None):
        """Recursive method for resolving a certificate. This starts with the
        data for a certificate, and a possible child certificate that needs to
        be validated. This is a reversed approach as the process is to start
        with a issued certificate and validate it upwards, until the root
        CA is reached.

        :param data: PEM encoded certificate to resolve.
        :param child: Optional child to validate.
        :raise PartialChainError: if no AIA is found, or the complete chain
                                  cannot be retreived. The exception contains
                                  the partial result.
        """
        result = []
        extension = x509.AuthorityInformationAccess
        oid = x509.oid.AuthorityInformationAccessOID

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
                'Could not verify certificate chain '
                '({} not signed by {})'.format(
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
                    r = requests.get(uri)
                    r.raise_for_status()

                    parent = self._resolve_chain(r.text, cert)

                    if parent:
                        result.extend(parent)
        except x509.ExtensionNotFound as e:
            raise PartialChainError('Missing AIA', result) from e
        except requests.exceptions.RequestException as e:
            raise PartialChainError(e, result) from e
        except InvalidSignature as e:
            raise PartialChainError(e, result) from e

        return result
