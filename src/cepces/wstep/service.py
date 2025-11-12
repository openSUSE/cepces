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
# pylint: disable=protected-access
"""Module for WSTEP SOAP service logic."""
from xml.etree import ElementTree
import uuid
import re
from cepces import Base
from cepces.soap.service import Service as SOAPService
from cepces.soap.types import Envelope
from cepces.wstep import QUERY_REQUEST_TYPE, NS_ENROLLMENT
from cepces.wstep.types import SecurityTokenRequest
from cepces.wstep.types import SecurityTokenResponseCollection

ACTION = (
    "http://schemas.microsoft.com/windows/pki/2009/01/enrollment/" "RST/wstep"
)


class Service(SOAPService):
    """WSTEP Service proxy."""

    class Response(Base):
        """Inner class for a service response."""

        def __init__(self, request_id, token=None, reference=None):
            super().__init__()

            self._request_id = request_id
            self._token = token
            self._reference = reference

        @property
        def request_id(self):
            """Returns the request ID."""
            return self._request_id

        @property
        def token(self):
            """Returns the response token."""
            return self._token

        @token.setter
        def token(self, value):
            """Sets the response token."""
            self._token = value

        @property
        def reference(self):
            """Returns the response reference."""
            return self._reference

    def _get_envelope(self, payload):
        envelope = Envelope()
        envelope.header.action = ACTION
        envelope.header.message_id = "urn:uuid:{0:s}".format(str(uuid.uuid4()))
        envelope.header.to = self._endpoint
        envelope.body.payload = payload._element

        self._logger.debug(
            "Preparing message %s to %s with payload: %s",
            envelope.header.message_id,
            envelope.header.to,
            ElementTree.tostring(payload._element),
        )

        return envelope

    def request(self, csr):
        """Request a certificate using a certificate signing request."""
        match = re.search(
            r"^\-{5}BEGIN (?:NEW )?CERTIFICATE REQUEST\-{5}\n"
            r"(.*)\n"
            r"\-{5}END (?:NEW )?CERTIFICATE REQUEST\-{5}\s*$",
            csr,
            flags=re.DOTALL,
        )

        if not match:
            raise LookupError("Invalid CSR.")

        token = SecurityTokenRequest()
        token.token = match.group(1)

        envelope = self._get_envelope(token)
        response = self.send(envelope)

        result = SecurityTokenResponseCollection(response.body.payload)

        # All responses has to be processed before hand, since they need to be
        # curated of any (possible) extra Microsoft-added line endings.
        results = []

        for response in result.responses:
            self._logger.debug("Got response: %s", str(response))

            token = response.requested_token

            if token.text:
                token.text = token.text.replace("&#xD;", "")

                results.append(
                    Service.Response(
                        request_id=response.request_id,
                        token=token.text,
                    ),
                )
            else:
                results.append(
                    Service.Response(
                        request_id=response.request_id,
                        reference=(
                            response.requested_token.token_reference.reference.uri  # noqa: E501
                        ),
                    ),
                )

        self._logger.debug("Returning curated responses: %s", results)

        return results

    def poll(self, request_id):
        """Poll the service endpoint for the status of a previous request."""
        self._logger.debug("Sending info for previous request %s", request_id)

        token = SecurityTokenRequest()
        token.request_type = QUERY_REQUEST_TYPE

        # Improve this handling since we're manually inserting an element here.
        qname = ElementTree.QName(NS_ENROLLMENT, "RequestID")
        element = ElementTree.Element(qname)  # type: ignore[type-var]
        token._element.append(element)
        token.request_id = request_id

        envelope = self._get_envelope(token)
        response = self.send(envelope)

        result = SecurityTokenResponseCollection(response.body.payload)

        # All responses has to be processed before hand, since they need to be
        # curated of any (possible) extra Microsoft-added line endings.
        results = []

        for response in result.responses:
            self._logger.debug("Got response: %s", response)

            token = response.requested_token

            if token.text:
                token.text = token.text.replace("&#xD;", "")

                results.append(
                    Service.Response(
                        request_id=response.request_id,
                        token=token.text,
                    ),
                )
            else:
                results.append(
                    Service.Response(
                        request_id=response.request_id,
                        reference=(
                            response.requested_token.token_reference.reference.uri  # noqa: E501
                        ),
                    ),
                )

        self._logger.debug("Returning curated responses: %s", results)

        return results
