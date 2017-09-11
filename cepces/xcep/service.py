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
from cepces.soap.service import Service as SOAPService
from cepces.soap.types import Envelope
from cepces.xcep.types import GetPolicies as GetPoliciesMessage
from cepces.xcep.types import GetPoliciesResponse as GetPoliciesResponseMessage
from xml.etree import ElementTree
import uuid

ACTION = 'http://schemas.microsoft.com/windows/pki/2009/01/enrollmentpolicy/' \
         'IPolicy/GetPolicies'


class Service(SOAPService):
    def _get_envelope(self, payload):
        envelope = Envelope()
        envelope.header.action = ACTION
        envelope.header.message_id = 'urn:uuid:{0:s}'.format(str(uuid.uuid4()))
        envelope.header.to = self._endpoint
        envelope.body.payload = payload._element

        self._logger.debug(
            "Preparing message {} to {} with payload: {}".format(
                envelope.header.message_id,
                envelope.header.to,
                ElementTree.tostring(payload._element),
            )
        )

        return envelope

    def get_policies(self):
        envelope = self._get_envelope(GetPoliciesMessage())
        response = self.send(envelope)

        self._logger.debug(
            "Received message: {}".format(
                ElementTree.tostring(response.body.payload),
            )
        )

        return GetPoliciesResponseMessage(response.body.payload)
