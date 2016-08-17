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
from cepces.binding import NS_XSI
from cepces.binding import XMLElement
from cepces.binding import XMLNode
from cepces.binding import XMLValue
from cepces.binding.converter import StringConverter
from requests_kerberos import HTTPKerberosAuth
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import QName
import logging
import requests

logger = logging.getLogger(__name__)

NS_SOAP = 'http://www.w3.org/2003/05/soap-envelope'
NS_ADDRESSING = 'http://www.w3.org/2005/08/addressing'


class Service(object):
    def __init__(self, endpoint, auth=None, capath=True):
        logger.debug("Initializing service (endpoint: %s, auth: %s", endpoint,
                     auth)
        self._endpoint = endpoint

        if auth == 'kerberos':
            # This step has been extended to work around issue #942 in the
            # kerberos library where the default principal cannot be
            # derived without raising an error. An explicit principal has
            # to be provided.
            #
            # This is ignored if PyKerberos is used.
            from urllib.parse import urlparse
            import kerberos

            if 'authGSSClientInquireCred' in dir(kerberos):
                parse = urlparse(endpoint)
                kerb_spn = "{0}@{1}".format("HTTP", parse.netloc)
                _, krb_context = kerberos.authGSSClientInit(kerb_spn)
                kerberos.authGSSClientInquireCred(krb_context)
                principal = kerberos.authGSSClientUserName(krb_context)
                # kerberos.authGSSClientClean(krb_context)
                auth = HTTPKerberosAuth(principal=principal)
            else:
                auth = HTTPKerberosAuth()

        self._auth = auth
        self._capath = capath

    def send(self, message):
        headers = {'Content-Type': 'application/soap+xml; charset=utf-8'}
        data = ElementTree.tostring(message._element)
        logger.debug("Sending message:")
        logger.debug("  url: %s", self._endpoint)
        logger.debug("  headers: %s", headers)
        logger.debug("  verify: %s", self._capath)
        logger.debug("  auth: %s", self._auth)
        logger.debug("  data: %s", data)

        # Post the envelope and raise an error if necessary.
        r = requests.post(url=self._endpoint,
                          data=data,
                          headers=headers,
                          verify=self._capath,
                          auth=self._auth)
        r.raise_for_status()

        # Blindly convert the response.
        envelope = ElementTree.fromstring(r.text)
        logger.debug("Received message: %s", envelope)
        return envelope


class Header(XMLNode):
    action = XMLValue('Action',
                      converter=StringConverter,
                      namespace=NS_ADDRESSING,
                      nillable=True)

    message_id = XMLValue('MessageID',
                          converter=StringConverter,
                          namespace=NS_ADDRESSING,
                          nillable=True)

    to = XMLValue('To',
                  converter=StringConverter,
                  namespace=NS_ADDRESSING,
                  nillable=True)

    @staticmethod
    def create():
        header = Element(QName(NS_SOAP, 'Header'))

        action = Element(QName(NS_ADDRESSING, 'Action'))
        action.attrib[QName(NS_SOAP, 'mustUnderstand')] = '1'
        action.attrib[QName(NS_XSI, 'nil')] = 'true'
        header.append(action)

        message_id = Element(QName(NS_ADDRESSING, 'MessageID'))
        message_id.attrib[QName(NS_XSI, 'nil')] = 'true'
        header.append(message_id)

        to = Element(QName(NS_ADDRESSING, 'To'))
        to.attrib[QName(NS_SOAP, 'mustUnderstand')] = '1'
        to.attrib[QName(NS_XSI, 'nil')] = 'true'
        header.append(to)

        return header


class Body(XMLNode):
    payload = XMLElement('*',
                         binder=None,
                         required=False)

    @staticmethod
    def create():
        body = Element(QName(NS_SOAP, 'Body'))

        return body


class Envelope(XMLNode):
    header = XMLElement('Header',
                        binder=Header,
                        namespace=NS_SOAP)

    body = XMLElement('Body',
                      binder=Body,
                      namespace=NS_SOAP)

    @staticmethod
    def create():
        envelope = Element(QName(NS_SOAP, 'Envelope'))
        envelope.append(Header.create())
        envelope.append(Body.create())

        return envelope
