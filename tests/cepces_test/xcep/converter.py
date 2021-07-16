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
import cepces.xcep.converter as converter


class TestClientAuthenticationConverter(TestCase):
    def testFromNone(self):
        """None as input should return None"""
        input = None
        c = converter.ClientAuthenticationConverter

        self.assertIsNone(c.from_string(input))

    def testFromString(self):
        """Valid input integer strings should return the correct string"""
        c = converter.ClientAuthenticationConverter

        for i in range(len(converter.ClientAuthenticationConverter.MAP)):
            result = c.from_string(str(1 << i))

            self.assertEqual(
                converter.ClientAuthenticationConverter.MAP[i][1],
                result,
                msg="{} should return {}".format(
                    str(i),
                    converter.ClientAuthenticationConverter.MAP[i][1],
                ),
            )
            self.assertIs(
                type(result),
                str,
                msg="{} should be of type str".format(str(i)),
            )

    def testToNone(self):
        """None as input should return None"""
        input = None
        result = converter.IntegerConverter.to_string(input)

        self.assertIsNone(result)

    def testToString(self):
        """A valid string should yield the correct stringified integer"""
        c = converter.ClientAuthenticationConverter

        for i in range(len(converter.ClientAuthenticationConverter.MAP)):
            value = converter.ClientAuthenticationConverter.MAP[i]
            result = c.to_string(value[1])

            self.assertEqual(type(result), str)
            self.assertEqual(result, str(value[0]))
