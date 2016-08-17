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
from cepces.binding import ATTR_NIL
from cepces.binding import XMLElement
from cepces.binding import XMLElementList
from cepces.binding import XMLNode
from cepces.binding import XMLValue
from cepces.binding import XMLValueList
from cepces.binding.converter import DateTimeConverter
from cepces.binding.converter import UnsignedIntegerConverter
from cepces.binding.converter import IntegerConverter
from cepces.binding.converter import SignedIntegerConverter
from cepces.binding.converter import StringConverter
from cepces.xcep.converter import ClientAuthenticationConverter
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import QName

NS_CEP = 'http://schemas.microsoft.com/windows/pki/2009/01/enrollmentpolicy'


class Client(XMLNode):
    ''' The `Client` node contains information about the client's current state
     and preferences.'''
    last_update = XMLValue('lastUpdate',
                           converter=DateTimeConverter,
                           namespace=NS_CEP,
                           nillable=True)
    preferred_language = XMLValue('preferredLanguage',
                                  converter=StringConverter,
                                  namespace=NS_CEP,
                                  nillable=True)

    @staticmethod
    def create():
        client = Element(QName(NS_CEP, 'client'))

        last_update = Element(QName(NS_CEP, 'lastUpdate'))
        last_update.attrib[ATTR_NIL] = 'true'
        client.append(last_update)

        preferred_language = Element(QName(NS_CEP, 'preferredLanguage'))
        preferred_language.attrib[ATTR_NIL] = 'true'
        client.append(preferred_language)

        return client


class RequestFilter(XMLNode):
    '''The `RequestFilter` node is provided in a request and used by the
    server to filter the `GetPoliciesResponse` to contain only
    `CertificateEnrollmentPolicy` objects that satisfy the filter.'''
    policy_oids = XMLValueList('policyOIDs',
                               child_name='oid',
                               converter=StringConverter,
                               namespace=NS_CEP,
                               child_namespace=NS_CEP,
                               nillable=True)
    client_version = XMLValue('clientVersion',
                              converter=SignedIntegerConverter,
                              namespace=NS_CEP,
                              nillable=True)
    server_version = XMLValue('serverVersion',
                              converter=SignedIntegerConverter,
                              namespace=NS_CEP,
                              nillable=True, required=False)

    @staticmethod
    def create():
        element = Element(QName(NS_CEP, 'requestFilter'))

        policy_oids = Element(QName(NS_CEP, 'policyOIDs'))
        policy_oids.attrib[ATTR_NIL] = 'true'
        element.append(policy_oids)

        client_version = Element(QName(NS_CEP, 'clientVersion'))
        client_version.attrib[ATTR_NIL] = 'true'
        element.append(client_version)

        server_version = Element(QName(NS_CEP, 'serverVersion'))
        server_version.attrib[ATTR_NIL] = 'true'
        element.append(server_version)

        return element


class GetPolicies(XMLNode):
    '''The `GetPolicies` node contains the client request.'''
    client = XMLElement('client',
                        binder=Client,
                        namespace=NS_CEP)
    request_filter = XMLElement('requestFilter',
                                binder=RequestFilter,
                                namespace=NS_CEP,
                                nillable=True)

    @staticmethod
    def create():
        element = Element(QName(NS_CEP, 'GetPolicies'))
        element.append(Client.create())
        element.append(RequestFilter.create())

        return element


class CertificateAuthorityURI(XMLNode):
    # The <clientAuthentication> element is used to define the supported
    # authentication type for the <uri> element of this CAURI object. The
    # <clientAuthentication> element is an unsigned integer that MUST have one
    # of the following values.
    #
    #   1: Anonymous Authentication
    #   2: Transport Kerberos Authentication
    #   4: Message Username and Password Authentication
    #   8: Message X.509 Certificate Authentication
    #
    # <xs:element name="clientAuthentication" type="xs:unsignedInt" />
    id = XMLValue('clientAuthentication',
                  converter=ClientAuthenticationConverter,
                  namespace=NS_CEP)

    # The <uri> element is used to store a Uniform Resource Identifier (URI)
    # entry for a CA (section 3.1.4.1.3.2) object.
    #
    # <xs:element name="uri" type="xs:anyURI" />
    uri = XMLValue('uri',
                   converter=StringConverter,
                   namespace=NS_CEP)

    # The <priority> element is an integer value that represents the priority
    # value for the URI. The <priority> element value is used as a relative
    # indicator against other CAURI objects. The lower the integer value, the
    # higher the priority. Two CAURI objects have the same priority if the
    # integer values of each <priority> element are the same. A CAURI object
    # is considered to have a lower priority if the <priority> element integer
    # value is more than the integer value of the <priority> element of an
    # alternate CAURI object.
    #
    # <xs:element name="priority" type="xs:unsignedInt" nillable="true" />
    priority = XMLValue('priority',
                        converter=UnsignedIntegerConverter,
                        namespace=NS_CEP,
                        nillable=True)


class CertificateAuthority(XMLNode):
    # An instance of a CAURICollection object as defined in section
    # 3.1.4.1.3.6, which contains the list of URI values for a certificate
    # authority.
    #
    # <xs:element name="uris" type="xcep:CAURICollection" />
    # <xs:element name="cAURI" type="xcep:CAURI"
    #  minOccurs="1" maxOccurs="unbounded" />
    uris = XMLElementList('uris',
                          child_name='cAURI',
                          binder=CertificateAuthorityURI,
                          namespace=NS_CEP,
                          child_namespace=NS_CEP)

    # Each instance of a CA object in a GetPoliciesResponse message MUST have a
    # unique <cAReferenceID>. The <cAReferenceID> is an unsigned integer value
    # used as an index for referencing the corresponding CA object within the
    # scope of a GetPoliciesResponse message.
    #
    # <xs:element name="cAReferenceID" type="xs:int" />
    id = XMLValue('cAReferenceID',
                  converter=SignedIntegerConverter,
                  namespace=NS_CEP)


class Attributes(XMLNode):
    # A string value of the common name (CN) of a CertificateEnrollmentPolicy
    # object. The <xcep:commonName> element MUST be unique in the scope of a
    # GetPoliciesResponse (section 3.1.4.1.1.2) message.
    #
    # <xs:element ref="xcep:commonName" />
    # <xs:element name="commonName" type="xs:string" />
    common_name = XMLValue('commonName',
                           converter=StringConverter,
                           namespace=NS_CEP)


class CertificateEnrollmentPolicy(XMLNode):
    # A <cAs> element is used to represent an instance of a
    # CAReferenceCollection object as defined in section 3.1.4.1.3.4, which is
    # used to reference the issuers for this CertificateEnrollmentPolicy
    # object.
    #
    # <xs:element name="cAs" type="CAReferenceCollection"
    #  nillable="true" />
    cas = XMLValueList('cAs',
                       child_name='cAReference',
                       converter=IntegerConverter,
                       namespace=NS_CEP,
                       child_namespace=NS_CEP,
                       nillable=True)

    # attributes: A <attributes> element is used to represent an instance of an
    # Attributes object as defined in section 3.1.4.1.3.1.
    #
    # <xs:element name="attributes" type="Attributes" />
    attributes = XMLElement('attributes',
                            binder=Attributes,
                            namespace=NS_CEP,
                            nillable=True)


class Response(XMLNode):
    # A unique identifier for the certificate enrollment policy. Two or more
    # servers can respond with the same <policyID> element in a
    # GetPoliciesResponse message if, and only if, they are configured to
    # return the same Response object to the same requestor. The <policyID>
    # element is not intended to be a human-readable property.
    #
    # <xs:element name="policyID" type="xs:string" />
    id = XMLValue('policyID',
                  converter=StringConverter,
                  namespace=NS_CEP)

    # A human readable friendly name for the certificate enrollment policy.
    #
    # <xs:element name="policyFriendlyName" type="xs:string" nillable="true" />
    name = XMLValue('policyFriendlyName',
                    converter=StringConverter,
                    namespace=NS_CEP,
                    nillable=True)

    # An integer representing the number of hours that the server recommends
    # the client wait before submitting another GetPolicies message. If the
    # <nextUpdateHours> element is present and not nil, the <nextUpdateHours>
    # element value MUST be a positive nonzero integer.
    #
    # <xs:element name="nextUpdateHours" type="xs:unsignedInt"
    #   nillable="true" />
    next_update = XMLValue('nextUpdateHours',
                           converter=UnsignedIntegerConverter,
                           namespace=NS_CEP,
                           nillable=True)

    # Used to indicate to the requestor whether the policies have changed since
    # the requestor specified <lastUpdateTime> in the GetPolicies request
    # message as described in section 3.1.4.1.3.9. If the value of the
    # <policiesNotChanged> element is true, the policy has not changed since
    # the <lastUpdateTime> value in the GetPolicies message. If the
    # <policiesNotChanged> element is false or nil, the policy has changed
    # since the requestor specified <lastUpdateTime>.
    #
    # <xs:element name="policiesNotChanged" type="xs:boolean"
    #   nillable="true" />
    policies_not_changed = XMLValue('policiesNotChanged',
                                    converter=UnsignedIntegerConverter,
                                    namespace=NS_CEP,
                                    nillable=True)

    # A list of policies.
    #
    # <xs:element name="policies" type="xcep:PolicyCollection"
    #   nillable="true" />
    # <xs:element name="policy" type="xcep:CertificateEnrollmentPolicy"
    #   minOccurs="1" maxOccurs="unbounded" />
    policies = XMLElementList('policies',
                              child_name='policy',
                              binder=CertificateEnrollmentPolicy,
                              namespace=NS_CEP,
                              child_namespace=NS_CEP,
                              nillable=True)


class GetPoliciesResponse(XMLNode):
    # The <xcep:response:> element is an instance of the Response object as
    # defined in section 3.1.4.1.3.23 that contains the certificate enrollment
    # policies.
    #
    # <xs:element name="response" nillable="true" type="xcep:Response" />
    response = XMLElement('response',
                          binder=Response,
                          namespace=NS_CEP,
                          nillable=True)

    # The <xcep:cAs> element is an instance of a CACollection object as defined
    # in section 3.1.4.1.3.3 that contains the issuers for the certificate
    # enrollment policies.
    #
    # <xs:element name="cAs" nillable="true" type="xcep:CACollection" />
    # <xs:element name="cA" type="xcep:CA" minOccurs="1"
    #   maxOccurs="unbounded" />
    cas = XMLElementList('cAs',
                         child_name='cA',
                         binder=CertificateAuthority,
                         namespace=NS_CEP,
                         child_namespace=NS_CEP,
                         nillable=True)
