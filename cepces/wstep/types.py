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
from cepces.soap import NS_ADDRESSING
from cepces.binding import XMLElement
from cepces.binding import XMLElementList
from cepces.binding import XMLValue
from cepces.binding import XMLNode
from cepces.binding.converter import StringConverter
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import QName

TOKEN_TYPE = 'http://docs.oasis-open.org/wss/2004/01/' \
             'oasis-200401-wss-x509-token-profile-1.0#X509v3'
REQUEST_TYPE = 'http://docs.oasis-open.org/ws-sx/ws-trust/200512/Issue'
VALUE_TYPE = 'http://schemas.microsoft.com/windows/pki/2009/01/' \
             'enrollment#PKCS10'
ENCODING_TYPE = 'http://docs.oasis-open.org/wss/2004/01/' \
                'oasis-200401-wss-wssecurity-secext-1.0.xsd#base64binary'

NS_WST = 'http://docs.oasis-open.org/ws-sx/ws-trust/200512'
NS_WST_SECEXT = 'http://docs.oasis-open.org/wss/2004/01/' \
                'oasis-200401-wss-wssecurity-secext-1.0.xsd'
NS_ENROLLMENT = 'http://schemas.microsoft.com/windows/pki/2009/01/enrollment'


class SecurityTokenRequest(XMLNode):
    # <xs:element ref='wst:TokenType' minOccurs='0' />
    token_type = XMLValue('TokenType',
                          converter=StringConverter,
                          namespace=NS_WST,
                          required=False)

    request_type = XMLValue('RequestType',
                            converter=StringConverter,
                            namespace=NS_WST)

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
        request_type.text = REQUEST_TYPE
        element.append(request_type)

        token = Element(QName(NS_WST_SECEXT, 'BinarySecurityToken'))
        token.set(QName(NS_WST_SECEXT, 'ValueType'), VALUE_TYPE)
        token.set(QName(NS_WST_SECEXT, 'EncodingType'), ENCODING_TYPE)
        token.set(QName(NS_ADDRESSING, 'Id'), '')
        element.append(token)

        return element


class RequestedToken(XMLNode):
    text = XMLValue('BinarySecurityToken',
                    converter=StringConverter,
                    namespace=NS_WST_SECEXT)


class SecurityTokenResponse(XMLNode):
    # <xs:element ref='wst:TokenType' minOccurs='0' />
    token_type = XMLValue('TokenType',
                          converter=StringConverter,
                          namespace=NS_WST,
                          required=False)

    disposition_message = XMLValue('DispositionMessage',
                                   converter=StringConverter,
                                   namespace=NS_ENROLLMENT)

    token = XMLElement('RequestedSecurityToken',
                       binder=RequestedToken,
                       namespace=NS_WST)


class SecurityTokenResponseCollection(XMLNode):
    responses = XMLElementList('.',
                               child_name='RequestSecurityTokenResponse',
                               binder=SecurityTokenResponse,
                               child_namespace=NS_WST)
