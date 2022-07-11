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
# pylint: disable=invalid-name
"""This module contains common SOAP types."""
from xml.etree.ElementTree import Element, QName
from cepces.soap import NS_ADDRESSING, NS_SOAP, NS_WSSE
from cepces.xml import NS_XSI
from cepces.xml.binding import XMLElement, XMLNode, XMLValue
from cepces.xml.converter import StringConverter


class FaultSubcode(XMLNode):
    """SOAP Fault Subcode."""
    value = XMLValue('Value',
                     converter=StringConverter,
                     namespace=NS_SOAP)

    @staticmethod
    def create():
        element = Element(QName(NS_SOAP, 'Subcode'))

        value = Element(QName(NS_SOAP, 'Value'))
        element.append(value)

        return element


class FaultCode(XMLNode):
    """SOAP Fault Code."""
    value = XMLValue('Value',
                     converter=StringConverter,
                     namespace=NS_SOAP)

    subcode = XMLElement('Subcode',
                         binder=FaultSubcode,
                         namespace=NS_SOAP)

    @staticmethod
    def create():
        element = Element(QName(NS_SOAP, 'Code'))

        value = Element(QName(NS_SOAP, 'Value'))
        element.append(value)

        element.append(FaultSubcode.create())

        return element


class FaultReason(XMLNode):
    """SOAP Fault Reason."""
    text = XMLValue('Text',
                    converter=StringConverter,
                    namespace=NS_SOAP)

    @staticmethod
    def create():
        element = Element(QName(NS_SOAP, 'Reason'))

        value = Element(QName(NS_SOAP, 'Text'))
        element.append(value)

        return element


class Fault(XMLNode):
    """SOAP Fault."""
    code = XMLElement('Code',
                      binder=FaultCode,
                      namespace=NS_SOAP)

    reason = XMLElement('Reason',
                        binder=FaultReason,
                        namespace=NS_SOAP)

    @staticmethod
    def create():
        element = Element(QName(NS_SOAP, 'Fault'))
        element.append(FaultCode.create())
        element.append(FaultReason.create())

        return element


class UsernameToken(XMLNode):
    """WSSE UsernameToken."""
    username = XMLValue('Username',
                     converter=StringConverter,
                     namespace=NS_WSSE)
    password = XMLValue('Password',
                     converter=StringConverter,
                     namespace=NS_WSSE)

    @staticmethod
    def create():
        usernametoken = Element(QName(NS_WSSE, 'UsernameToken'))
 
        username = Element(QName(NS_WSSE, 'Username'))
        usernametoken.append(username)

        password = Element(QName(NS_WSSE, 'Password'))
        password.attrib[QName(NS_WSSE, 'Type' )] = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText'
        usernametoken.append(password)

        return usernametoken


class Security(XMLNode):
    """WSSE Security."""
    usernametoken = XMLElement('UsernameToken',
                        binder=UsernameToken,
                        namespace=NS_WSSE)

    @staticmethod
    def create():
        security = Element(QName(NS_WSSE, 'Security'))
        security.attrib[QName(NS_SOAP, 'mustUnderstand')] = '1'

        return security


class Header(XMLNode):
    """SOAP Header."""
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

    relates_to = XMLValue('RelatesTo',
                          converter=StringConverter,
                          namespace=NS_ADDRESSING,
                          nillable=True)

    security =  XMLElement ('Security',
                            binder=Security,
                            namespace=NS_WSSE)

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
    """SOAP Body."""
    payload = XMLElement('*',
                         binder=None,
                         required=False)

    @staticmethod
    def create():
        body = Element(QName(NS_SOAP, 'Body'))

        return body


class Envelope(XMLNode):
    """SOAP Envelope."""
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
