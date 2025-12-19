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
"""Module containing user cert enroll logic."""
import os
from pyasn1.codec.der.encoder import encode
from pyasn1.type import char
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import (
    ed25519,
    ed448,
    rsa,
    dsa,
    ec,
    types,
)
from cepces.config import Configuration
from cepces.core import Service


class ApprovalPendingException(Exception):
    def __init__(self, request_id, reference, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_id = request_id
        self.reference = reference


class UserEnrollment:
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.service = self._init_service(*args, **kwargs)

    def _init_service(self, global_overrides=None, krb5_overrides=None):
        # Load the configuration and instantiate a service.
        config = Configuration.load(
            global_overrides=global_overrides, krb5_overrides=krb5_overrides
        )

        return Service(config)

    def request(self, key_file, cert_file, profile, keysize, passphrase):
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                tmp_key = serialization.load_pem_private_key(
                    f.read(),
                    password=passphrase.encode() if passphrase else None,
                    backend=default_backend(),
                )
                if isinstance(
                    tmp_key,
                    (
                        ed25519.Ed25519PrivateKey,
                        ed448.Ed448PrivateKey,
                        rsa.RSAPrivateKey,
                        dsa.DSAPrivateKey,
                        ec.EllipticCurvePrivateKey,
                    ),
                ):
                    key: types.CertificateIssuerPrivateKeyTypes = tmp_key
                else:
                    raise Exception("Unsupported key type")
        else:
            print(str(key_file) + " does not exist, generating a new key...")
            key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=int(keysize),
            )
            enc: serialization.KeySerializationEncryption = (
                serialization.NoEncryption()
            )
            if passphrase:
                enc = serialization.BestAvailableEncryption(
                    passphrase.encode()
                )
            with open(
                os.open(key_file, os.O_CREAT | os.O_WRONLY, 0o400), "wb"
            ) as f:
                f.write(
                    key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.TraditionalOpenSSL,
                        encryption_algorithm=enc,
                    )
                )

        csr = x509.CertificateSigningRequestBuilder().subject_name(
            x509.Name(
                [
                    x509.NameAttribute(NameOID.COMMON_NAME, profile),
                ]
            )
        )
        csr = csr.add_extension(
            x509.UnrecognizedExtension(
                oid=x509.ObjectIdentifier("1.3.6.1.4.1.311.20.2"),
                value=encode(char.BMPString(profile)),
            ),
            critical=False,
        )

        result = self.service.request(
            csr.sign(key, hashes.SHA256()),
            renew=None,
        )

        self._check_result(result, cert_file)

    def poll(self, cert_file, request_id, reference):
        result = self.service.poll(int(request_id), reference)
        self._check_result(result, cert_file)

    def _check_result(self, result, cert_file):
        # if we have a certificate, save it
        if result.token:
            pem = result.token.public_bytes(serialization.Encoding.PEM)

            with open(cert_file, "w") as f:
                f.write(pem.decode().strip())
                print("Certificate written to:", cert_file)
            return

        # return a "cookie" that can be used to later poll the status
        raise ApprovalPendingException(result.request_id, result.reference)
