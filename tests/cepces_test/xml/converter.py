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
import cepces.xml.converter as converter
import pytest


def test_string_converter_from_none():
    """None as input should return None"""
    input = None
    result = converter.StringConverter.from_string(input)

    assert result is None


def test_string_converter_from_string():
    """A string as input should return an equal string"""
    input = "TestString"
    result = converter.StringConverter.from_string(input)

    assert input == result


def test_string_converter_to_none():
    """None as input should return None"""
    input = None
    result = converter.StringConverter.to_string(input)

    assert result is None


def test_string_converter_to_string():
    """A string as input should return an equal string"""
    input = "TestString"
    result = converter.StringConverter.to_string(input)

    assert str(input) == result


def test_boolean_converter_from_none():
    """None as input should return None"""
    input = None
    result = converter.BooleanConverter.from_string(input)

    assert result is None


def test_boolean_converter_from_string():
    """Boolean strings as input should return a boolean"""
    c = converter.BooleanConverter

    assert c.from_string("true")
    assert c.from_string("1")
    assert not c.from_string("false")
    assert not c.from_string("0")


def test_boolean_converter_to_none():
    """None as input should return None"""
    input = None
    result = converter.BooleanConverter.to_string(input)

    assert result is None


def test_boolean_converter_to_string():
    """A boolean as input should return an equal boolean (lower) string"""
    c = converter.BooleanConverter

    assert "true" == c.to_string(True)
    assert "false" == c.to_string(False)


def test_integer_converter_from_none():
    """None as input should return None"""
    input = None
    result = converter.IntegerConverter.from_string(input)

    assert result is None


def test_integer_converter_from_string():
    """An integer string as input should return an integer"""
    input = 4711
    result = converter.IntegerConverter.from_string(str(input))

    assert input == result


def test_integer_converter_to_none():
    """None as input should return None"""
    input = None
    result = converter.IntegerConverter.to_string(input)

    assert result is None


def test_integer_converter_to_string():
    """An integer as input should return an equal integer string"""
    input = 4711
    result = converter.IntegerConverter.to_string(input)

    assert str(input) == result


def test_ranged_integer_converter_from_none():
    """None as input should return None"""
    input = None
    result = converter.RangedIntegerConverter.from_string(input, 0, 1)

    assert result is None


def test_ranged_integer_converter_from_string():
    """An integer string as input should return a valid integer"""
    f = converter.RangedIntegerConverter.from_string

    assert 10 == f(str(10), 0, 20)
    with pytest.raises(ValueError):
        f(str(-1), 0, 20)
    with pytest.raises(ValueError):
        f(str(21), 0, 20)


def test_ranged_integer_converter_to_none():
    """None as input should return None"""
    input = None
    result = converter.RangedIntegerConverter.to_string(input, 0, 1)

    assert result is None


def test_ranged_integer_converter_to_string():
    """An integer as input should return an equal integer string"""
    f = converter.RangedIntegerConverter.to_string

    assert str(10) == f(10, 0, 20)
    with pytest.raises(ValueError):
        f(-1, 0, 20)
    with pytest.raises(ValueError):
        f(21, 0, 20)


def test_signed_integer_converter_from_none():
    """None as input should return None"""
    input = None
    result = converter.SignedIntegerConverter.from_string(input)

    assert result is None


def test_signed_integer_converter_from_string():
    """An integer string as input should return a valid integer"""
    f = converter.SignedIntegerConverter.from_string

    assert 10 == f(str(10))
    with pytest.raises(ValueError):
        f(str(-(2**31) - 1))
    with pytest.raises(ValueError):
        f(str(2**31))


def test_signed_integer_converter_to_none():
    """None as input should return None"""
    input = None
    result = converter.SignedIntegerConverter.to_string(input)

    assert result is None


def test_signed_integer_converter_to_string():
    """An integer as input should return an equal integer string"""
    f = converter.SignedIntegerConverter.to_string

    assert str(10) == f(10)
    with pytest.raises(ValueError):
        f(-(2**31) - 1)
    with pytest.raises(ValueError):
        f(2**31)


def test_unsigned_integer_converter_from_none():
    """None as input should return None"""
    input = None
    result = converter.UnsignedIntegerConverter.from_string(input)

    assert result is None


def test_unsigned_integer_converter_from_string():
    """An integer string as input should return a valid integer"""
    f = converter.UnsignedIntegerConverter.from_string

    assert 10 == f(str(10))
    with pytest.raises(ValueError):
        f(str(-1))
    with pytest.raises(ValueError):
        f(str(2**32))


def test_unsigned_integer_converter_to_none():
    """None as input should return None"""
    input = None
    result = converter.UnsignedIntegerConverter.to_string(input)

    assert result is None


def test_unsigned_integer_converter_to_string():
    """An integer as input should return an equal integer string"""
    f = converter.UnsignedIntegerConverter.to_string

    assert str(10) == f(10)
    with pytest.raises(ValueError):
        f(-1)
    with pytest.raises(ValueError):
        f(2**32)


# TODO: Implement TestDateTimeConverter
