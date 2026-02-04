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
import cepces.xcep.converter as converter


def test_client_authentication_converter_from_none() -> None:
    """None as input should return None"""
    input = None
    c = converter.ClientAuthenticationConverter

    assert c.from_string(input) is None


def test_client_authentication_converter_from_string() -> None:
    """Valid input integer strings should return the correct string"""
    c = converter.ClientAuthenticationConverter

    for i in range(len(converter.ClientAuthenticationConverter.MAP)):
        result = c.from_string(str(1 << i))

        assert converter.ClientAuthenticationConverter.MAP[i][1] == result, (
            "{} should return {}".format(
                str(i),
                converter.ClientAuthenticationConverter.MAP[i][1],
            )
        )
        assert isinstance(result, str), "{} should be of type str".format(
            str(i)
        )


def test_client_authentication_converter_to_none() -> None:
    """None as input should return None"""
    input = None
    result = converter.IntegerConverter.to_string(input)

    assert result is None


def test_client_authentication_converter_to_string() -> None:
    """A valid string should yield the correct stringified integer"""
    c = converter.ClientAuthenticationConverter

    for i in range(len(converter.ClientAuthenticationConverter.MAP)):
        value = converter.ClientAuthenticationConverter.MAP[i]
        # ClientAuthenticationConverter.to_string intentionally overrides
        # parent to accept str instead of int (see type: ignore[override]
        # in converter)
        result = c.to_string(value[1])  # type: ignore[arg-type]

        assert isinstance(result, str)
        assert result == str(value[0])
