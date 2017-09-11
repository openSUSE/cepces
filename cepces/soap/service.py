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
# This module contains SOAP related classes, implementing a loose subset of the
# specification, just enough to be able to communicate a service.
#
from cepces.core import Base
from cepces.soap import ACTION_FAULT
from cepces.soap.types import Envelope, Fault
from xml.etree import ElementTree
import requests


class SOAPFault(Exception):
    def __init__(self, fault):
        self._code = fault.code.value
        self._subcode = fault.code.subcode.value
        self._reason = fault.reason.text

        msg = "{} (Code: {}; Subcode: {})".format(
            self._reason,
            self._code,
            self._subcode,
        )

        super().__init__(msg)


class Service(Base):
    def __init__(self, endpoint, auth=None, capath=True):
        super().__init__()

        self._logger.debug(
            "Initializing service (endpoint: {}, auth: {}".format(
                endpoint, auth)
        )
        self._endpoint = endpoint
        self._auth = auth
        self._capath = capath

    def send(self, message):
        headers = {'Content-Type': 'application/soap+xml; charset=utf-8'}
        data = ElementTree.tostring(message._element)

        self._logger.debug("Sending message:")
        self._logger.debug(" -endpoint: %s", self._endpoint)
        self._logger.debug(" -headers: %s", headers)
        self._logger.debug(" -verify: %s", self._capath)
        self._logger.debug(" -auth: %s", self._auth)
        self._logger.debug(" -data: %s", data)

        # Post process the envelope.
        if self._auth:
            message = self._auth.post_process(message)

        # Post the envelope and raise an error if necessary.
        r = requests.post(url=self._endpoint,
                          data=data,
                          headers=headers,
                          verify=self._capath,
                          auth=self._auth.transport)

        # If we get an internal server error (code 500), there's a chance that
        # we get a SOAP Envelope back containing a SOAP Fault.
        if not r.status_code == requests.codes.internal_server_error:
            r.raise_for_status()

        # Convert the response.
        element = ElementTree.fromstring(r.text)
        envelope = Envelope(element)
        self._logger.debug("Received message: %s", envelope._element)

        # Throw a SOAP fault if one was received. Otherwise, raise a generic
        # exception from requests.
        if r.status_code == requests.codes.internal_server_error and \
           envelope.header.action == ACTION_FAULT:
            fault = Fault(envelope.body.payload)

            raise SOAPFault(fault)
        else:
            r.raise_for_status()

        return envelope
