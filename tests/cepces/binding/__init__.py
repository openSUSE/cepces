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
import unittest
from cepces.binding import ListingMeta
from cepces.binding import XMLDescriptor
from cepces.binding import XMLNode
from xml.etree import ElementTree


class MockXMLDescriptor(XMLDescriptor):
    def __get__(self, instance, _owner=None):
        return instance._test_value

    def __set__(self, instance, value):
        instance._test_value = value

    def __delete__(self, instance):
        pass


class TestXMLDescriptor(unittest.TestCase):
    def testOnlyName(self):
        """Qualified name should be equal to name"""
        descriptor = MockXMLDescriptor('name')

        self.assertEqual(descriptor._name, 'name')
        self.assertEqual(descriptor._namespace, None)
        self.assertEqual(descriptor._qname, 'name')

    def testNameAndNameSpace(self):
        """Qualified name should be in Clark's notation"""
        descriptor = MockXMLDescriptor('name', 'namespace')

        self.assertEqual(descriptor._name, 'name')
        self.assertEqual(descriptor._namespace, 'namespace')
        self.assertEqual(descriptor._qname, '{namespace}name')

    def testIndexIncrement(self):
        """Static index should increase accordingly"""
        index = XMLDescriptor._index

        # Create three descriptors..
        first = MockXMLDescriptor('first')
        second = MockXMLDescriptor('second')
        third = MockXMLDescriptor('third')

        self.assertEqual(first._index, index)
        self.assertEqual(second._index, index + 1)
        self.assertEqual(third._index, index + 2)
        self.assertEqual(XMLDescriptor._index, index + 3)


class TestListingMeta(unittest.TestCase):
    def setUp(self):
        super().setUp()

        # Create a dummy class.
        class MockClass(metaclass=ListingMeta):
            first = MockXMLDescriptor('first')
            second = MockXMLDescriptor('second')
            third = MockXMLDescriptor('third')

        self._dummy = MockClass

    def testListingAttribute(self):
        self.assertTrue(hasattr(self._dummy, '__listing__'))

    def testOrderedListing(self):
        dummy = self._dummy
        listing = dummy.__listing__

        self.assertEqual(listing[0][0], 'first')
        self.assertEqual(listing[1][0], 'second')
        self.assertEqual(listing[2][0], 'third')

        self.assertEqual(listing[0][1], dummy.__dict__[listing[0][0]])
        self.assertEqual(listing[1][1], dummy.__dict__[listing[1][0]])
        self.assertEqual(listing[2][1], dummy.__dict__[listing[2][0]])

    def tearDown(self):
        super().tearDown()

        self._dummy = None


if __name__ == '__main__':
    unittest.main()
