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

"""Module containing core classes and functionality."""


from cepces import Base
from cepces import auth
from cepces.xcep.service import Service as XCEPService
from cepces.wstep.service import Service as WSTEPService
from cepces.soap import auth as SOAPAuth
from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
import requests


class Configuration(Base):
    AUTH_HANDLER_MAP = {
        'Anonymous': auth.AnonymousAuthenticationHandler,
        'Kerberos': auth.KerberosAuthenticationHandler,
        'UsernamePassword': auth.UsernamePasswordAuthenticationHandler,
        'Certificate': auth.CertificateAuthenticationHandler,
    }

    AUTH_MAP = {
        'Anonymous': SOAPAuth.AnonymousAuthentication,
        'Kerberos': SOAPAuth.TransportKerberosAuthentication,
        'UsernamePassword': SOAPAuth.MessageUsernamePasswordAuthentication,
        'Certificate': SOAPAuth.MessageCertificateAuthentication,
    }

    def __init__(self, endpoint, cas, auth):
        self._endpoint = endpoint
        self._cas = cas
        self._auth = auth

    @property
    def endpoint(self):
        return self._endpoint

    @property
    def cas(self):
        return self._cas

    @property
    def auth(self):
        return self._auth

    @classmethod
    def from_parser(cls, parser):
        # Ensure there's a global section present.
        if 'global' not in parser:
            raise RuntimeError('Missing "global" section in configuration.')

        section = parser['global']

        # Ensure certain required variables are present.
        for var in ['endpoint', 'auth']:
            if var not in section:
                raise RuntimeError(
                    'Missing "{}/{}" variable in configuration.'.format(
                        'global',
                        var,
                    ),
                )

        # Verify that the chosen authentication method is valid.
        if section['auth'] not in Configuration.AUTH_HANDLER_MAP.keys():
            raise RuntimeError(
                'No such authentication method: {}'.format(
                    section['auth'],
                ),
            )

        # Store the global configuration options.
        endpoint = section.get('endpoint')
        auth = Configuration.AUTH_HANDLER_MAP[section['auth']](parser).handle()
        cas = section.get('cas', True)

        if cas == '':
            cas = False

        return Configuration(endpoint, cas, auth)


class PartialChainError(RuntimeError):
    def __init__(self, msg, result):
        super().__init__(msg)
        self._result = result

    @property
    def result(self):
        return self._result


class Service(Base):
    class Endpoint(Base):
        def __init__(self, url, priority, renewal_only):
            self._url = url
            self._priority = priority
            self._renewal_only = renewal_only

        @property
        def url(self):
            return self._url

        @property
        def priority(self):
            return self._priority

        @property
        def renewal_only(self):
            return self._renewal_only

        def __str__(self):
            return self.url

    def __init__(self, config):
        super().__init__()

        self._config = config
        self._xcep = XCEPService(
            config.endpoint,
            config.auth,
            config.cas,
        )

        # Eagerly load the policy response.
        self._policies = self._xcep.get_policies()

    @property
    def templates(self):
        """Retrieve a list of available templates."""
        templates = []

        for policy in self._policies.response.policies:
            templates.append(policy.attributes.common_name)

        return templates

    @property
    def endpoints(self):
        """Retrieves a list of WSTEP suitable endpoints."""
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

        return [x for x in sorted(endpoints, key=lambda x: x.priority)]

    @property
    def certificate_chain(self, index=0):
        """Get the complete certification authority chain.

        This retreives the certificate from the issuing endpoint service, and
        then uses the AIA information to retreive the rest of the chain.

        :raise PartialChainError: if no AIA is found, or the complete chain
                                  cannot be retreived. The exception contains
                                  the partial result.
        """
        # Get the first certificate. Since is (or at least always should) be
        # securely retreived over a secure channel, only verify subsequent
        # certificates.
        data = self._policies.cas[index].certificate

        return reversed(self._resolve_chain(data))

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
        cert = x509.load_pem_x509_certificate(
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
        except x509.ExtensionNotFound:
            raise PartialChainError('Missing AIA', result)
        except requests.exceptions.RequestException as e:
            raise PartialChainError(e, result)
        except InvalidSignature as e:
            raise PartialChainError(e, result)

        return result
