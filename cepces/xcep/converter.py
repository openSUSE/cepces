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
from cepces.binding.converter import Converter


class ClientAuthenticationConverter(Converter):
    MAP = [
        (1, 'anonymous'),
        (2, 'kerberos'),
        (4, 'userpass'),
        (8, 'certificate')
    ]

    @staticmethod
    def from_string(value):
        values = [v[0] for v in ClientAuthenticationConverter.MAP]

        if value is None:
            return value
        elif not isinstance(value, str):
            raise TypeError('Unsupported type.')
        elif int(value) not in values:
            raise ValueError('Unsupported value.')
        else:
            index = values.index(int(value))
            return ClientAuthenticationConverter.MAP[index][1]

    @staticmethod
    def to_string(value):
        values = [v[1] for v in ClientAuthenticationConverter.MAP]

        if value is None:
            return None
        elif not isinstance(value, str):
            raise TypeError('Unsupported type.')
        elif value not in values:
            raise ValueError('Unsupported value.')
        else:
            index = values.index(value)
            return str(ClientAuthenticationConverter.MAP[index][0])
