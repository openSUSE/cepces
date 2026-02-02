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
from cepces.soap import NS_ADDRESSING, NS_SOAP, NS_WSSE, NS_WSU
from cepces.xml import NS_XSI
from cepces.xml.binding import XMLElement, XMLNode, XMLValue
from cepces.xml.converter import StringConverter, DateTimeConverter


class FaultSubcode(XMLNode):
    """SOAP Fault Subcode."""

    value = XMLValue("Value", converter=StringConverter, namespace=NS_SOAP)

    @staticmethod
    def create() -> Element:
        element = Element(QName(NS_SOAP, "Subcode"))  # type: ignore[type-var]

        value = Element(QName(NS_SOAP, "Value"))  # type: ignore[type-var]
        element.append(value)

        return element


class FaultCode(XMLNode):
    """SOAP Fault Code."""

    value = XMLValue("Value", converter=StringConverter, namespace=NS_SOAP)

    subcode = XMLElement("Subcode", binder=FaultSubcode, namespace=NS_SOAP)

    @staticmethod
    def create() -> Element:
        element = Element(QName(NS_SOAP, "Code"))  # type: ignore[type-var]

        value = Element(QName(NS_SOAP, "Value"))  # type: ignore[type-var]
        element.append(value)

        element.append(FaultSubcode.create())

        return element


class FaultReason(XMLNode):
    """SOAP Fault Reason."""

    text = XMLValue("Text", converter=StringConverter, namespace=NS_SOAP)

    @staticmethod
    def create() -> Element:
        element = Element(QName(NS_SOAP, "Reason"))  # type: ignore[type-var]

        value = Element(QName(NS_SOAP, "Text"))  # type: ignore[type-var]
        element.append(value)

        return element


class Fault(XMLNode):
    """SOAP Fault."""

    code = XMLElement("Code", binder=FaultCode, namespace=NS_SOAP)

    reason = XMLElement("Reason", binder=FaultReason, namespace=NS_SOAP)

    @staticmethod
    def create() -> Element:
        element = Element(QName(NS_SOAP, "Fault"))  # type: ignore[type-var]
        element.append(FaultCode.create())
        element.append(FaultReason.create())

        return element


class UsernameToken(XMLNode):
    """WSSE UsernameToken."""

    username = XMLValue(
        "Username", converter=StringConverter, namespace=NS_WSSE
    )
    password = XMLValue(
        "Password", converter=StringConverter, namespace=NS_WSSE
    )
    nonce = XMLValue("Nonce", converter=StringConverter, namespace=NS_WSSE)
    created = XMLValue(
        "Created", converter=DateTimeConverter, namespace=NS_WSU
    )

    @staticmethod
    def create() -> Element:
        usernametoken = Element(QName(NS_WSSE, "UsernameToken"))  # type: ignore[type-var]  # noqa: E501

        username = Element(QName(NS_WSSE, "Username"))  # type: ignore[type-var]  # noqa: E501
        usernametoken.append(username)

        password = Element(QName(NS_WSSE, "Password"))  # type: ignore[type-var]  # noqa: E501
        password.attrib[QName(NS_WSSE, "Type")] = (  # type: ignore[index]
            "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText"  # noqa: E501
        )
        # password.attrib[QName(NS_WSSE, 'Type' )] = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordDigest'  # noqa: E501
        usernametoken.append(password)

        nonce = Element(QName(NS_WSSE, "Nonce"))  # type: ignore[type-var]
        usernametoken.append(nonce)

        created = Element(QName(NS_WSU, "Created"))  # type: ignore[type-var]
        usernametoken.append(created)

        return usernametoken


class Security(XMLNode):
    """WSSE Security."""

    usernametoken = XMLElement(
        "UsernameToken", binder=UsernameToken, namespace=NS_WSSE
    )

    @staticmethod
    def create() -> Element:
        security = Element(QName(NS_WSSE, "Security"))  # type: ignore[type-var]  # noqa: E501
        security.attrib[QName(NS_SOAP, "mustUnderstand")] = "1"  # type: ignore[index]  # noqa: E501

        return security


class Header(XMLNode):
    """SOAP Header."""

    action = XMLValue(
        "Action",
        converter=StringConverter,
        namespace=NS_ADDRESSING,
        nillable=True,
    )

    message_id = XMLValue(
        "MessageID",
        converter=StringConverter,
        namespace=NS_ADDRESSING,
        nillable=True,
    )

    to = XMLValue(
        "To", converter=StringConverter, namespace=NS_ADDRESSING, nillable=True
    )

    relates_to = XMLValue(
        "RelatesTo",
        converter=StringConverter,
        namespace=NS_ADDRESSING,
        nillable=True,
    )

    security = XMLElement("Security", binder=Security, namespace=NS_WSSE)

    @staticmethod
    def create() -> Element:
        header = Element(QName(NS_SOAP, "Header"))  # type: ignore[type-var]

        action = Element(QName(NS_ADDRESSING, "Action"))  # type: ignore[type-var]  # noqa: E501
        action.attrib[QName(NS_SOAP, "mustUnderstand")] = "1"  # type: ignore[index]  # noqa: E501
        action.attrib[QName(NS_XSI, "nil")] = "true"  # type: ignore[index]
        header.append(action)

        message_id = Element(QName(NS_ADDRESSING, "MessageID"))  # type: ignore[type-var]  # noqa: E501
        message_id.attrib[QName(NS_XSI, "nil")] = "true"  # type: ignore[index]  # noqa: E501
        header.append(message_id)

        to = Element(QName(NS_ADDRESSING, "To"))  # type: ignore[type-var]
        to.attrib[QName(NS_SOAP, "mustUnderstand")] = "1"  # type: ignore[index]  # noqa: E501
        to.attrib[QName(NS_XSI, "nil")] = "true"  # type: ignore[index]
        header.append(to)

        return header


class Body(XMLNode):
    """SOAP Body."""

    payload = XMLElement("*", binder=None, required=False)

    @staticmethod
    def create() -> Element:
        body = Element(QName(NS_SOAP, "Body"))  # type: ignore[type-var]

        return body


class Envelope(XMLNode):
    """SOAP Envelope."""

    header = XMLElement("Header", binder=Header, namespace=NS_SOAP)

    body = XMLElement("Body", binder=Body, namespace=NS_SOAP)

    @staticmethod
    def create() -> Element:
        envelope = Element(QName(NS_SOAP, "Envelope"))  # type: ignore[type-var]  # noqa: E501
        envelope.append(Header.create())
        envelope.append(Body.create())

        return envelope
