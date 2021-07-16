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
from unittest import TestCase
import cepces.xml.converter as converter


class TestStringConverter(TestCase):
    def testFromNone(self):
        """None as input should return None"""
        input = None
        result = converter.StringConverter.from_string(input)

        self.assertIsNone(result)

    def testFromString(self):
        """A string as input should return an equal string"""
        input = 'TestString'
        result = converter.StringConverter.from_string(input)

        self.assertEqual(input, result)

    def testToNone(self):
        """None as input should return None"""
        input = None
        result = converter.StringConverter.to_string(input)

        self.assertIsNone(result)

    def testToString(self):
        """A string as input should return an equal string"""
        input = 'TestString'
        result = converter.StringConverter.to_string(input)

        self.assertEqual(str(input), result)


class TestBooleanConverter(TestCase):
    def testFromNone(self):
        """None as input should return None"""
        input = None
        result = converter.BooleanConverter.from_string(input)

        self.assertIsNone(result)

    def testFromString(self):
        """Boolean strings as input should return a boolean"""
        c = converter.BooleanConverter

        self.assertEqual(True, c.from_string('true'))
        self.assertEqual(True, c.from_string('1'))
        self.assertEqual(False, c.from_string('false'))
        self.assertEqual(False, c.from_string('0'))

    def testToNone(self):
        """None as input should return None"""
        input = None
        result = converter.BooleanConverter.to_string(input)

        self.assertIsNone(result)

    def testToString(self):
        """A boolean as input should return an equal boolean (lower) string"""
        c = converter.BooleanConverter

        self.assertEqual('true', c.to_string(True))
        self.assertEqual('false', c.to_string(False))


class TestIntegerConverter(TestCase):
    def testFromNone(self):
        """None as input should return None"""
        input = None
        result = converter.IntegerConverter.from_string(input)

        self.assertIsNone(result)

    def testFromString(self):
        """An integer string as input should return an integer"""
        input = 4711
        result = converter.IntegerConverter.from_string(str(input))

        self.assertEqual(input, result)

    def testToNone(self):
        """None as input should return None"""
        input = None
        result = converter.IntegerConverter.to_string(input)

        self.assertIsNone(result)

    def testToString(self):
        """An integer as input should return an equal integer string"""
        input = 4711
        result = converter.IntegerConverter.to_string(input)

        self.assertEqual(str(input), result)


class TestRangedIntegerConverter(TestCase):
    def testFromNone(self):
        """None as input should return None"""
        input = None
        result = converter.RangedIntegerConverter.from_string(input, 0, 1)

        self.assertIsNone(result)

    def testFromString(self):
        """An integer string as input should return a valid integer"""
        f = converter.RangedIntegerConverter.from_string

        self.assertEqual(10, f(str(10), 0, 20))
        self.assertRaises(ValueError, f, str(-1), 0, 20)
        self.assertRaises(ValueError, f, str(21), 0, 20)

    def testToNone(self):
        """None as input should return None"""
        input = None
        result = converter.RangedIntegerConverter.to_string(input, 0, 1)

        self.assertIsNone(result)

    def testToString(self):
        """An integer as input should return an equal integer string"""
        f = converter.RangedIntegerConverter.to_string

        self.assertEqual(str(10), f(10, 0, 20))
        self.assertRaises(ValueError, f, -1, 0, 20)
        self.assertRaises(ValueError, f, 21, 0, 20)


class TestSignedIntegerConverter(TestCase):
    def testFromNone(self):
        """None as input should return None"""
        input = None
        result = converter.SignedIntegerConverter.from_string(input)

        self.assertIsNone(result)

    def testFromString(self):
        """An integer string as input should return a valid integer"""
        f = converter.SignedIntegerConverter.from_string

        self.assertEqual(10, f(str(10)))
        self.assertRaises(ValueError, f, str(-2 ** 31 - 1))
        self.assertRaises(ValueError, f, str(2 ** 31))

    def testToNone(self):
        """None as input should return None"""
        input = None
        result = converter.SignedIntegerConverter.to_string(input)

        self.assertIsNone(result)

    def testToString(self):
        """An integer as input should return an equal integer string"""
        f = converter.SignedIntegerConverter.to_string

        self.assertEqual(str(10), f(10))
        self.assertRaises(ValueError, f, -2 ** 31 - 1)
        self.assertRaises(ValueError, f, 2 ** 31)


class TestUnsignedIntegerConverter(TestCase):
    def testFromNone(self):
        """None as input should return None"""
        input = None
        result = converter.UnsignedIntegerConverter.from_string(input)

        self.assertIsNone(result)

    def testFromString(self):
        """An integer string as input should return a valid integer"""
        f = converter.UnsignedIntegerConverter.from_string

        self.assertEqual(10, f(str(10)))
        self.assertRaises(ValueError, f, str(-1))
        self.assertRaises(ValueError, f, str(2 ** 32))

    def testToNone(self):
        """None as input should return None"""
        input = None
        result = converter.UnsignedIntegerConverter.to_string(input)

        self.assertIsNone(result)

    def testToString(self):
        """An integer as input should return an equal integer string"""
        f = converter.UnsignedIntegerConverter.to_string

        self.assertEqual(str(10), f(10))
        self.assertRaises(ValueError, f, -1)
        self.assertRaises(ValueError, f, 2 ** 32)


class TestDateTimeConverter(TestCase):
    # TODO
    pass
