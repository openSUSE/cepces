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


class TestXMLDescriptor(unittest.TestCase):
    def testOnlyName(self):
        '''Qualified name should be equal to name'''
        descriptor = XMLDescriptor('name')

        self.assertEqual(descriptor._name, 'name')
        self.assertEqual(descriptor._namespace, None)
        self.assertEqual(descriptor._qname, 'name')

    def testNameAndNameSpace(self):
        '''Qualified name should be in Clark's notation'''
        descriptor = XMLDescriptor('name', 'namespace')

        self.assertEqual(descriptor._name, 'name')
        self.assertEqual(descriptor._namespace, 'namespace')
        self.assertEqual(descriptor._qname, '{namespace}name')

    def testIndexIncrement(self):
        '''Static index should increase accordingly'''
        index = XMLDescriptor._index

        class MockClass():
            # Create three descriptors..
            first = XMLDescriptor('first')
            second = XMLDescriptor('second')
            third = XMLDescriptor('third')

        # Make sure the index has incremented accordingly.
        self.assertEqual(XMLDescriptor._index, index + 3)


class TestListingMeta(unittest.TestCase):
    def setUp(self):
        super(TestListingMeta, self).setUp()

        # Create a dummy class.
        class MockClass(metaclass=ListingMeta):
            first = XMLDescriptor('first')
            second = XMLDescriptor('second')
            third = XMLDescriptor('third')

        self._dummy = MockClass

    def testListingAttribute(self):
        self.assertTrue(hasattr(self._dummy, '__listing__'))

    def testOrderedListing(self):
        dummy = self._dummy
        listing = dummy.__listing__

        self.assertEqual(listing[0][0], 'first')
        self.assertEqual(listing[1][0], 'second')
        self.assertEqual(listing[2][0], 'third')

        self.assertEqual(listing[0][1], dummy.first)
        self.assertEqual(listing[1][1], dummy.second)
        self.assertEqual(listing[2][1], dummy.third)

    def tearDown(self):
        super(TestListingMeta, self).tearDown()

        self._dummy = None


class TestXMLNode(unittest.TestCase):
    def setUp(self):
        super(TestXMLNode, self).setUp()

        self.element = ElementTree.Element('root')
        self.node = XMLNode(self.element)

    def testValidConstructorArgument(self):
        '''Test should not fail with valid constructor argument'''
        self.assertIsInstance(self.node, XMLNode)
        self.assertEqual(self.node._bindings, {})
        self.assertIs(self.node._element, self.element)

    def testInvalidConstructorArgument(self):
        '''Test should fail with invalid constructor argument'''
        self.assertRaises(TypeError, XMLNode, 'string')

    def testInvalidConstructorElement(self):
        '''Test should fail with empty node'''
        self.assertRaises(NotImplementedError, XMLNode, None)

    def testCreate(self):
        '''Test should fail on abstract method'''
        self.assertRaises(NotImplementedError, self.node.create)
