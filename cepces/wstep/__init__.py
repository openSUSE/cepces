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
from cepces.soap import Service as SOAPService
from cepces.soap import Envelope
from cepces.soap import Body
from cepces.wstep.types import SecurityTokenRequest
from cepces.wstep.types import SecurityTokenResponseCollection
from xml.etree import ElementTree
import logging
import uuid
import re

logger = logging.getLogger(__name__)

ACTION = 'http://schemas.microsoft.com/windows/pki/2009/01/enrollment/' \
         'RST/wstep'


class Service(SOAPService):
    def get_envelope(self, payload):
        envelope = Envelope()
        envelope.header.action = ACTION
        envelope.header.message_id = "urn:uuid:{0:s}".format(str(uuid.uuid4()))
        envelope.header.to = self._endpoint
        envelope.body.payload = payload._element

        logger.debug('Preparing message %s to %s with payload: %s',
                     envelope.header.message_id,
                     envelope.header.to,
                     ElementTree.tostring(payload._element))

        return envelope

    def request(self, csr):
        m = re.search('^\-{5}BEGIN NEW CERTIFICATE REQUEST\-{5}\n'
                      '(.*)\n'
                      '\-{5}END NEW CERTIFICATE REQUEST\-{5}\s*$',
                      csr,
                      flags=re.DOTALL)

        if not m:
            raise LookupError('Invalid CSR.')

        token = SecurityTokenRequest()
        token.token = m.group(1)

        envelope = self.get_envelope(token)
        result = self.send(envelope)

        # if result is None:
        #     raise LookupError('No responses.')
        soap_response = Envelope(result)
        response = SecurityTokenResponseCollection(soap_response.body.payload)

        # All responses has to be processed before hand, since they need to be
        # curated of any (possible) extra Microsoft-added line endings.
        for r in response.responses:
            r.token.text = r.token.text.replace('&#xD;', '')

        return response.responses
