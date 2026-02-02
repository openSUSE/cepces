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
"""Module containing XCEP related type converters."""

from cepces.xml.converter import IntegerConverter


class ClientAuthenticationConverter(IntegerConverter):
    """Converts to and from allowed authentication methods (int <-> str)."""

    MAP = [
        (1, "Anonymous"),
        (2, "Kerberos"),
        (4, "UsernamePassword"),
        (8, "Certificate"),
    ]

    # This method intentionally returns str instead of int - it converts
    # integer auth values to authentication method names.
    @staticmethod
    def from_string(value):  # type: ignore[override]
        """Converts the stringified integer key to its string value

        :param value: the stringified integer to convert, or None
        :raise TypeError: if the input is not a string
        :raise ValueError: if the input cannot be resolved
        :return: the input as a string value, or None if value is None
        """
        values = [v[0] for v in ClientAuthenticationConverter.MAP]

        if value is None:
            return value
        elif not isinstance(value, str):
            raise TypeError("Unsupported type.")
        elif int(value) not in values:
            raise ValueError("Unsupported value.")
        else:
            index = values.index(int(value))

            return ClientAuthenticationConverter.MAP[index][1]

    @staticmethod
    def to_string(value):
        """Converts the string value its stringified integer

        :param value: the string to convert, or None
        :raise TypeError: if the input is not a string
        :raise ValueError: if the input cannot be resolved
        :return: the input as a string value, or None if value is None
        """
        values = [v[1] for v in ClientAuthenticationConverter.MAP]

        if value is None:
            return None
        elif not isinstance(value, str):
            raise TypeError("Unsupported type.")
        elif value not in values:
            raise ValueError("Unsupported value.")
        else:
            index = values.index(value)

            return str(ClientAuthenticationConverter.MAP[index][0])
