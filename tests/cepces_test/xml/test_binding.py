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
import pytest
from xml.etree import ElementTree
from cepces.xml.binding import ListingMeta
from cepces.xml.binding import XMLDescriptor
from cepces.xml.binding import XMLNode
from cepces.xml.binding import XMLElementList


class MockXMLDescriptor(XMLDescriptor):
    def __get__(self, instance, _owner=None):
        return instance._test_value

    def __set__(self, instance, value):
        instance._test_value = value

    def __delete__(self, instance):
        pass


def test_xml_descriptor_only_name():
    """Qualified name should be equal to name"""
    descriptor = MockXMLDescriptor("name")

    assert descriptor._name == "name"
    assert descriptor._namespace is None
    assert descriptor._qname == "name"


def test_xml_descriptor_name_and_namespace():
    """Qualified name should be in Clark's notation"""
    descriptor = MockXMLDescriptor("name", "namespace")

    assert descriptor._name == "name"
    assert descriptor._namespace == "namespace"
    assert descriptor._qname == "{namespace}name"


def test_xml_descriptor_index_increment():
    """Static index should increase accordingly"""
    index = XMLDescriptor._index

    # Create three descriptors..
    first = MockXMLDescriptor("first")
    second = MockXMLDescriptor("second")
    third = MockXMLDescriptor("third")

    assert first._index == index
    assert second._index == index + 1
    assert third._index == index + 2
    assert XMLDescriptor._index == index + 3


@pytest.fixture
def mock_class():
    """Create a dummy class for testing ListingMeta"""

    class MockClass(metaclass=ListingMeta):
        first = MockXMLDescriptor("first")
        second = MockXMLDescriptor("second")
        third = MockXMLDescriptor("third")

    return MockClass


def test_listing_meta_listing_attribute(mock_class):
    """Test that __listing__ attribute exists"""
    assert hasattr(mock_class, "__listing__")


def test_listing_meta_ordered_listing(mock_class):
    """Test that listing is ordered correctly"""
    dummy = mock_class
    listing = dummy.__listing__

    assert listing[0][0] == "first"
    assert listing[1][0] == "second"
    assert listing[2][0] == "third"

    assert listing[0][1] == dummy.__dict__[listing[0][0]]
    assert listing[1][1] == dummy.__dict__[listing[1][0]]
    assert listing[2][1] == dummy.__dict__[listing[2][0]]


class ChildNode(XMLNode):
    """A simple child node for testing XMLElementList."""

    @staticmethod
    def create():
        return ElementTree.Element("child")


class ParentNode(XMLNode):
    """A parent node with an XMLElementList that may be missing."""

    children = XMLElementList(
        "children",
        child_name="child",
        binder=ChildNode,
        nillable=True,
    )

    @staticmethod
    def create():
        return ElementTree.Element("parent")


def test_xml_element_list_missing_element_returns_none():
    """XMLElementList should return None when the element doesn't exist.

    This reproduces a bug where accessing .cas on a GetPoliciesResponse
    when no CAs element exists causes an IndexError because the code
    tries to create an XMLElementList.List with element=None.
    """
    # Create a parent element without the 'children' sub-element
    parent_element = ElementTree.Element("parent")
    parent_node = ParentNode(parent_element)

    # Accessing children should return None, not raise an error
    result = parent_node.children

    assert result is None


NS_XSI = "http://www.w3.org/2001/XMLSchema-instance"


@pytest.mark.xfail(reason="XMLElementList doesn't handle xsi:nil='true'")
def test_xml_element_list_nil_element_returns_none():
    """XMLElementList should return None when the element has xsi:nil='true'.

    This reproduces the bug from certmonger where accessing .cas on a
    GetPoliciesResponse with '<cAs xsi:nil="true" />' causes an IndexError
    because the code creates an empty list instead of returning None.

    Example XML that triggers this:
    <GetPoliciesResponse xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <cAs xsi:nil="true" />
    </GetPoliciesResponse>
    """
    # Create a parent element with a nil 'children' sub-element
    parent_element = ElementTree.Element("parent")
    children_element = ElementTree.SubElement(parent_element, "children")
    children_element.set(f"{{{NS_XSI}}}nil", "true")

    parent_node = ParentNode(parent_element)

    # Accessing children should return None when xsi:nil="true"
    result = parent_node.children

    assert result is None
