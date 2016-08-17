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
from cepces.xcep.types import GetPolicies as GetPoliciesMessage
from cepces.xcep.types import GetPoliciesResponse as GetPoliciesResponseMessage
from xml.etree import ElementTree
import logging
import uuid

logger = logging.getLogger(__name__)

ACTION = 'http://schemas.microsoft.com/windows/pki/2009/01/enrollmentpolicy/' \
         'IPolicy/GetPolicies'


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

    def get_policies(self):
        envelope = self.get_envelope(GetPoliciesMessage())
        result = self.send(envelope)
        response = Envelope(result)

        logger.debug('Received message: %s',
                     ElementTree.tostring(response.body.payload))

        return GetPoliciesResponseMessage(response.body.payload)

    def resolve(self, name, auth):
        '''Resolve the CES endpoint(s) for a given policy/template and
        authentication method.'''
        logger.debug('Resolving CEP endpoints.')
        result = self.get_policies()

        # Find policies with matching template name. It should always be zero
        # or one match as the common name MUST be unique.
        logger.debug('Found: %s', result.response.policies)

        policies = [p for p in result.response.policies
                    if p.attributes.common_name == name]

        logger.debug('Matching: %s', policies)

        if not policies:
            raise LookupError('No such certificate profile.')

        policy = policies[0]

        logger.debug('Issuing CAs: %s', policy.cas)

        if not policy.cas:
            raise LookupError('No CAs issuing the profile.')

        # Find all CAs issuing this template, order by priority.
        ids = [ca for ca in policy.cas]
        cas = [ca for ca in result.cas if ca.id in ids]
        prio = sorted([(uri.priority, uri.uri)
                       for ca in cas
                       for uri in ca.uris
                       if uri.id == auth], key=lambda x: x[0])
        endpoints = [uri[1] for uri in prio]

        logger.debug('Found potential endpoints: %s', endpoints)

        return endpoints
