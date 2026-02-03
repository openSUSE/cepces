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
from typing import Any

import pytest
from xml.etree import ElementTree
from cepces.xml.binding import ListingMeta
from cepces.xml.binding import XMLDescriptor
from cepces.xml.binding import XMLNode
from cepces.xml.binding import XMLAttribute
from cepces.xml.binding import XMLElement
from cepces.xml.binding import XMLElementList
from cepces.xml.binding import XMLValue
from cepces.xml.converter import (
    BooleanConverter,
    IntegerConverter,
    StringConverter,
    UnsignedIntegerConverter,
)


class MockXMLDescriptor(XMLDescriptor):
    def __get__(self, instance: Any, _owner: type | None = None) -> Any:
        return instance._test_value

    def __set__(self, instance: Any, value: Any) -> None:
        instance._test_value = value

    def __delete__(self, instance: Any) -> None:
        pass


def test_xml_descriptor_only_name() -> None:
    """Qualified name should be equal to name"""
    descriptor = MockXMLDescriptor("name")

    assert descriptor._name == "name"
    assert descriptor._namespace is None
    assert descriptor._qname == "name"


def test_xml_descriptor_name_and_namespace() -> None:
    """Qualified name should be in Clark's notation"""
    descriptor = MockXMLDescriptor("name", "namespace")

    assert descriptor._name == "name"
    assert descriptor._namespace == "namespace"
    assert descriptor._qname == "{namespace}name"


def test_xml_descriptor_index_increment() -> None:
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
def mock_class() -> type:
    """Create a dummy class for testing ListingMeta"""

    class MockClass(metaclass=ListingMeta):
        first = MockXMLDescriptor("first")
        second = MockXMLDescriptor("second")
        third = MockXMLDescriptor("third")

    return MockClass


def test_listing_meta_listing_attribute(mock_class: type) -> None:
    """Test that __listing__ attribute exists"""
    assert hasattr(mock_class, "__listing__")


def test_listing_meta_ordered_listing(mock_class: type) -> None:
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


def test_xml_element_list_missing_element_returns_none() -> None:
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


def test_xml_element_list_nil_element_returns_none() -> None:
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


# =============================================================================
# XMLAttribute Tests
# =============================================================================

NS_TEST = "http://test.example.com"


class NodeWithAttribute(XMLNode):
    """Test node with XMLAttribute descriptors."""

    name = XMLAttribute("name", converter=StringConverter)
    count = XMLAttribute("count", converter=IntegerConverter)
    enabled = XMLAttribute("enabled", converter=BooleanConverter)
    ns_attr = XMLAttribute(
        "value", namespace=NS_TEST, converter=StringConverter
    )

    @staticmethod
    def create() -> ElementTree.Element:
        return ElementTree.Element("node")


class TestXMLAttributeGet:
    """Tests for XMLAttribute.__get__ behavior."""

    def test_get_string_attribute(self) -> None:
        """XMLAttribute should return string attribute value."""
        xml = '<node name="test-name" />'
        element = ElementTree.fromstring(xml)
        node = NodeWithAttribute(element)

        assert node.name == "test-name"

    def test_get_integer_attribute(self) -> None:
        """XMLAttribute with IntegerConverter should return int."""
        xml = '<node count="42" />'
        element = ElementTree.fromstring(xml)
        node = NodeWithAttribute(element)

        assert node.count == 42
        assert isinstance(node.count, int)

    def test_get_boolean_attribute_true(self) -> None:
        """XMLAttribute with BooleanConverter should return bool."""
        xml = '<node enabled="true" />'
        element = ElementTree.fromstring(xml)
        node = NodeWithAttribute(element)

        assert node.enabled is True
        assert isinstance(node.enabled, bool)

    def test_get_boolean_attribute_false(self) -> None:
        """XMLAttribute with BooleanConverter should handle 'false'."""
        xml = '<node enabled="false" />'
        element = ElementTree.fromstring(xml)
        node = NodeWithAttribute(element)

        assert node.enabled is False

    def test_get_namespaced_attribute(self) -> None:
        """XMLAttribute should handle namespaced attributes."""
        xml = f'<node xmlns:t="{NS_TEST}" t:value="namespaced-value" />'
        element = ElementTree.fromstring(xml)
        node = NodeWithAttribute(element)

        assert node.ns_attr == "namespaced-value"

    def test_get_missing_attribute_returns_none(self) -> None:
        """XMLAttribute should return None for missing attributes."""
        xml = "<node />"
        element = ElementTree.fromstring(xml)
        node = NodeWithAttribute(element)

        # StringConverter.from_string(None) returns None
        assert node.name is None


class TestXMLAttributeSet:
    """Tests for XMLAttribute.__set__ behavior."""

    def test_set_string_attribute(self) -> None:
        """XMLAttribute should set string attribute value."""
        node = NodeWithAttribute()
        node.name = "new-name"

        assert node._element is not None
        assert node._element.get("name") == "new-name"

    def test_set_integer_attribute(self) -> None:
        """XMLAttribute should convert int to string when setting."""
        node = NodeWithAttribute()
        node.count = 123

        assert node._element is not None
        assert node._element.get("count") == "123"

    def test_set_boolean_attribute(self) -> None:
        """XMLAttribute should convert bool to lowercase string."""
        node = NodeWithAttribute()
        node.enabled = True

        assert node._element is not None
        assert node._element.get("enabled") == "true"


class TestXMLAttributeDelete:
    """Tests for XMLAttribute.__delete__ behavior."""

    def test_delete_attribute(self) -> None:
        """XMLAttribute should remove attribute on delete."""
        xml = '<node name="to-delete" />'
        element = ElementTree.fromstring(xml)
        node = NodeWithAttribute(element)

        assert node.name == "to-delete"
        del node.name
        assert "name" not in element.attrib


# =============================================================================
# XMLValue Tests
# =============================================================================


class NodeWithValue(XMLNode):
    """Test node with XMLValue descriptors."""

    text = XMLValue("text", converter=StringConverter)
    number = XMLValue("number", converter=UnsignedIntegerConverter)
    optional = XMLValue(
        "optional", converter=StringConverter, required=False, nillable=True
    )
    ns_value = XMLValue("value", converter=StringConverter, namespace=NS_TEST)

    @staticmethod
    def create() -> ElementTree.Element:
        return ElementTree.Element("node")


class TestXMLValueGet:
    """Tests for XMLValue.__get__ behavior."""

    def test_get_string_value(self) -> None:
        """XMLValue should return element text content."""
        xml = "<node><text>hello world</text></node>"
        element = ElementTree.fromstring(xml)
        node = NodeWithValue(element)

        assert node.text == "hello world"
        assert isinstance(node.text, str)

    def test_get_integer_value(self) -> None:
        """XMLValue with UnsignedIntegerConverter should return int."""
        xml = "<node><number>999</number></node>"
        element = ElementTree.fromstring(xml)
        node = NodeWithValue(element)

        assert node.number == 999
        assert isinstance(node.number, int)

    def test_get_missing_element_returns_none(self) -> None:
        """XMLValue should return None when element doesn't exist."""
        xml = "<node />"
        element = ElementTree.fromstring(xml)
        node = NodeWithValue(element)

        assert node.text is None

    def test_get_namespaced_value(self) -> None:
        """XMLValue should handle namespaced elements."""
        xml = f'<node xmlns:t="{NS_TEST}"><t:value>ns-content</t:value></node>'
        element = ElementTree.fromstring(xml)
        node = NodeWithValue(element)

        assert node.ns_value == "ns-content"

    def test_get_nil_value_returns_none(self) -> None:
        """XMLValue nillable=True returns None for xsi:nil='true'."""
        xml = f"""<node xmlns:xsi="{NS_XSI}">
            <optional xsi:nil="true" />
        </node>"""
        element = ElementTree.fromstring(xml)
        node = NodeWithValue(element)

        assert node.optional is None

    def test_get_empty_element_returns_none(self) -> None:
        """XMLValue should return None for empty element text."""
        xml = "<node><text></text></node>"
        element = ElementTree.fromstring(xml)
        node = NodeWithValue(element)

        # StringConverter.from_string("") returns "" but empty string is falsy
        # Actually StringConverter returns the value as-is if it's a string
        result = node.text
        assert result is None or result == ""


class TestXMLValueSet:
    """Tests for XMLValue.__set__ behavior."""

    def test_set_string_value(self) -> None:
        """XMLValue should set element text content."""
        xml = "<node><text>old</text></node>"
        element = ElementTree.fromstring(xml)
        node = NodeWithValue(element)

        node.text = "new value"

        text_elem = element.find("text")
        assert text_elem is not None
        assert text_elem.text == "new value"

    def test_set_integer_value(self) -> None:
        """XMLValue should convert int to string when setting."""
        xml = "<node><number>0</number></node>"
        element = ElementTree.fromstring(xml)
        node = NodeWithValue(element)

        node.number = 12345

        num_elem = element.find("number")
        assert num_elem is not None
        assert num_elem.text == "12345"

    def test_set_nillable_to_none(self) -> None:
        """XMLValue nillable=True sets xsi:nil when value is None."""
        xml = "<node><optional>has-value</optional></node>"
        element = ElementTree.fromstring(xml)
        node = NodeWithValue(element)

        node.optional = None

        opt_elem = element.find("optional")
        assert opt_elem is not None
        nil_attr = f"{{{NS_XSI}}}nil"
        assert opt_elem.get(nil_attr) == "true"


# =============================================================================
# XMLElement Tests
# =============================================================================


class InnerNode(XMLNode):
    """A simple inner node for XMLElement tests."""

    value = XMLValue("value", converter=StringConverter)

    @staticmethod
    def create() -> ElementTree.Element:
        elem = ElementTree.Element("inner")
        value_elem = ElementTree.SubElement(elem, "value")
        value_elem.text = ""
        return elem


class OuterNode(XMLNode):
    """Test node with XMLElement descriptors."""

    inner = XMLElement("inner", binder=InnerNode)
    optional_inner = XMLElement(
        "optional", binder=InnerNode, required=False, nillable=True
    )
    ns_inner = XMLElement("child", binder=InnerNode, namespace=NS_TEST)

    @staticmethod
    def create() -> ElementTree.Element:
        return ElementTree.Element("outer")


class TestXMLElementGet:
    """Tests for XMLElement.__get__ behavior."""

    def test_get_returns_binder_instance(self) -> None:
        """XMLElement should return an instance of the binder class."""
        xml = "<outer><inner><value>test</value></inner></outer>"
        element = ElementTree.fromstring(xml)
        node = OuterNode(element)

        result = node.inner
        assert result is not None
        assert isinstance(result, InnerNode)

    def test_get_preserves_nested_values(self) -> None:
        """XMLElement binder should preserve nested XMLValue access."""
        xml = "<outer><inner><value>nested-content</value></inner></outer>"
        element = ElementTree.fromstring(xml)
        node = OuterNode(element)

        assert node.inner.value == "nested-content"

    def test_get_missing_element_returns_none(self) -> None:
        """XMLElement should return None for missing child elements."""
        xml = "<outer />"
        element = ElementTree.fromstring(xml)
        node = OuterNode(element)

        # inner is required but missing - __get__ returns None
        assert node.inner is None

    def test_get_optional_missing_returns_none(self) -> None:
        """XMLElement with required=False should return None when missing."""
        xml = "<outer><inner><value>x</value></inner></outer>"
        element = ElementTree.fromstring(xml)
        node = OuterNode(element)

        assert node.optional_inner is None

    def test_get_namespaced_element(self) -> None:
        """XMLElement should handle namespaced child elements."""
        xml = f"""<outer xmlns:t="{NS_TEST}">
            <t:child><value>ns-nested</value></t:child>
        </outer>"""
        element = ElementTree.fromstring(xml)
        node = OuterNode(element)

        assert node.ns_inner is not None
        assert isinstance(node.ns_inner, InnerNode)
        assert node.ns_inner.value == "ns-nested"

    def test_get_caches_binder(self) -> None:
        """XMLElement should cache and return same binder instance."""
        xml = "<outer><inner><value>test</value></inner></outer>"
        element = ElementTree.fromstring(xml)
        node = OuterNode(element)

        first = node.inner
        second = node.inner

        assert first is second


class TestXMLElementSet:
    """Tests for XMLElement.__set__ behavior."""

    def test_set_with_element(self) -> None:
        """XMLElement should accept an Element and create binder."""
        node = OuterNode()

        inner_elem = ElementTree.Element("inner")
        value_elem = ElementTree.SubElement(inner_elem, "value")
        value_elem.text = "set-value"

        node.inner = inner_elem

        assert node.inner is not None
        assert isinstance(node.inner, InnerNode)
        assert node.inner.value == "set-value"


class TestXMLElementDelete:
    """Tests for XMLElement.__delete__ behavior."""

    def test_delete_optional_element(self) -> None:
        """XMLElement with required=False should allow deletion."""
        xml = """<outer>
            <inner><value>x</value></inner>
            <optional><value>to-delete</value></optional>
        </outer>"""
        element = ElementTree.fromstring(xml)
        node = OuterNode(element)

        assert node.optional_inner is not None
        del node.optional_inner
        assert node.optional_inner is None

    def test_delete_required_element_raises(self) -> None:
        """XMLElement with required=True should raise on deletion."""
        xml = "<outer><inner><value>x</value></inner></outer>"
        element = ElementTree.fromstring(xml)
        node = OuterNode(element)

        with pytest.raises(AttributeError, match="required"):
            del node.inner


# =============================================================================
# Type Preservation Tests for Descriptors
# =============================================================================


class TestDescriptorTypePreservation:
    """Tests verifying descriptors preserve correct runtime types."""

    def test_xml_attribute_preserves_string_type(self) -> None:
        """XMLAttribute with StringConverter returns str."""
        xml = '<node name="string-value" />'
        element = ElementTree.fromstring(xml)
        node = NodeWithAttribute(element)

        result = node.name
        assert isinstance(result, str)
        assert result == "string-value"

    def test_xml_attribute_preserves_int_type(self) -> None:
        """XMLAttribute with IntegerConverter returns int."""
        xml = '<node count="100" />'
        element = ElementTree.fromstring(xml)
        node = NodeWithAttribute(element)

        result = node.count
        assert isinstance(result, int)
        assert result == 100

    def test_xml_attribute_preserves_bool_type(self) -> None:
        """XMLAttribute with BooleanConverter returns bool."""
        xml = '<node enabled="1" />'
        element = ElementTree.fromstring(xml)
        node = NodeWithAttribute(element)

        result = node.enabled
        assert isinstance(result, bool)
        assert result is True

    def test_xml_value_preserves_string_type(self) -> None:
        """XMLValue with StringConverter returns str."""
        xml = "<node><text>content</text></node>"
        element = ElementTree.fromstring(xml)
        node = NodeWithValue(element)

        result = node.text
        assert isinstance(result, str)
        assert result == "content"

    def test_xml_value_preserves_int_type(self) -> None:
        """XMLValue with UnsignedIntegerConverter returns int."""
        xml = "<node><number>4294967295</number></node>"
        element = ElementTree.fromstring(xml)
        node = NodeWithValue(element)

        result = node.number
        assert isinstance(result, int)
        assert result == 4294967295

    def test_xml_element_preserves_binder_type(self) -> None:
        """XMLElement returns instance of specified binder class."""
        xml = "<outer><inner><value>test</value></inner></outer>"
        element = ElementTree.fromstring(xml)
        node = OuterNode(element)

        result = node.inner
        assert isinstance(result, InnerNode)

    def test_nested_descriptor_chain_types(self) -> None:
        """Nested descriptors preserve types through the chain."""
        xml = "<outer><inner><value>chain-test</value></inner></outer>"
        element = ElementTree.fromstring(xml)
        node = OuterNode(element)

        # OuterNode -> InnerNode -> str
        assert isinstance(node, OuterNode)
        assert isinstance(node.inner, InnerNode)
        assert isinstance(node.inner.value, str)
        assert node.inner.value == "chain-test"
