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
"""WSTEP Types."""
from xml.etree.ElementTree import Element, QName
from cepces.soap import NS_ADDRESSING
from cepces.wstep import NS_WST, NS_WST_SECEXT, NS_ENROLLMENT
from cepces.wstep import TOKEN_TYPE, VALUE_TYPE, ENCODING_TYPE
from cepces.wstep import ISSUE_REQUEST_TYPE
from cepces.xml.binding import XMLAttribute
from cepces.xml.binding import XMLElement, XMLElementList
from cepces.xml.binding import XMLNode, XMLValue
from cepces.xml.converter import CertificateConverter
from cepces.xml.converter import StringConverter, UnsignedIntegerConverter


class SecurityTokenRequest(XMLNode):
    """Security Token Request"""
    # <xs:element ref='wst:TokenType' minOccurs='0' />
    token_type = XMLValue('TokenType',
                          converter=StringConverter,
                          namespace=NS_WST,
                          required=False)

    request_type = XMLValue('RequestType',
                            converter=StringConverter,
                            namespace=NS_WST)

    request_id = XMLValue('RequestID',
                          converter=UnsignedIntegerConverter,
                          namespace=NS_ENROLLMENT)

    token = XMLValue('BinarySecurityToken',
                     converter=StringConverter,
                     namespace=NS_WST_SECEXT)

    @staticmethod
    def create():
        element = Element(QName(NS_WST, 'RequestSecurityToken'))

        token_type = Element(QName(NS_WST, 'TokenType'))
        token_type.text = TOKEN_TYPE
        element.append(token_type)

        request_type = Element(QName(NS_WST, 'RequestType'))
        request_type.text = ISSUE_REQUEST_TYPE
        element.append(request_type)

        token = Element(QName(NS_WST_SECEXT, 'BinarySecurityToken'))
        token.set(QName(NS_WST_SECEXT, 'ValueType'), VALUE_TYPE)
        token.set(QName(NS_WST_SECEXT, 'EncodingType'), ENCODING_TYPE)
        token.set(QName(NS_ADDRESSING, 'Id'), '')
        element.append(token)

        return element


class Reference(XMLNode):
    """Reference"""
    uri = XMLAttribute('URI',
                       converter=StringConverter)

    @staticmethod
    def create():
        return None


class SecurityTokenReference(XMLNode):
    """Security Token Reference"""
    reference = XMLElement('Reference',
                           binder=Reference,
                           namespace=NS_WST_SECEXT,
                           required=False)

    @staticmethod
    def create():
        return None


class RequestedToken(XMLNode):
    """Requested Token"""
    text = XMLValue('BinarySecurityToken',
                    converter=CertificateConverter,
                    namespace=NS_WST_SECEXT)

    token_reference = XMLElement('SecurityTokenReference',
                                 binder=SecurityTokenReference,
                                 namespace=NS_WST_SECEXT,
                                 required=False)

    @staticmethod
    def create():
        return None


class SecurityTokenResponse(XMLNode):
    """Security Token Response"""
    # <xs:element ref='wst:TokenType' minOccurs='0' />
    token_type = XMLValue('TokenType',
                          converter=StringConverter,
                          namespace=NS_WST,
                          required=False)

    disposition_message = XMLValue('DispositionMessage',
                                   converter=StringConverter,
                                   namespace=NS_ENROLLMENT)

    token = XMLValue('BinarySecurityToken',
                     converter=StringConverter,
                     namespace=NS_WST_SECEXT)

    requested_token = XMLElement('RequestedSecurityToken',
                                 binder=RequestedToken,
                                 namespace=NS_WST)

    request_id = XMLValue('RequestID',
                          converter=UnsignedIntegerConverter,
                          namespace=NS_ENROLLMENT)

    @staticmethod
    def create():
        return None


class SecurityTokenResponseCollection(XMLNode):
    """Security Token Response Collection"""
    responses = XMLElementList('.',
                               child_name='RequestSecurityTokenResponse',
                               binder=SecurityTokenResponse,
                               child_namespace=NS_WST)

    @staticmethod
    def create():
        return None
