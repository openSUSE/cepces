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
# pylint: disable=protected-access,too-few-public-methods,too-many-arguments
# pylint: disable=too-many-ancestors
"""Module containing XML bindings.

This module provides a descriptor-based system for binding Python objects
to XML elements. The descriptors use Python's Generic type system to
provide type inference for the values they return.

Type System Design:
- XMLElement[T]: Generic descriptor that returns instances of type T
  (typically an XMLNode subclass) when accessing child elements.
- XMLValue[T]: Generic descriptor that returns values of type T
  (e.g., str, int, bool) after converting element text content.
- XMLElementList[T]: Returns a mutable list of T instances.
- XMLValueList[T]: Returns a mutable list of T values.

The @overload decorators distinguish between:
- Class access (instance=None): Returns the descriptor itself
- Instance access: Returns T | None (the bound value or None if missing)
"""

from typing import Any, Callable, Generic, TypeVar, cast, overload
from collections.abc import MutableSequence
from xml.etree import ElementTree
import inspect
from abc import ABCMeta, abstractmethod
from cepces.xml import ATTR_NIL, NS_XSI, util
from cepces.xml.converter import ConverterProtocol, StringConverter

# TypeVar for generic descriptors - represents the type returned by the
# descriptor (e.g., an XMLNode subclass for XMLElement, or int for XMLValue
# with IntegerConverter).
T = TypeVar("T")


class XMLDescriptor(metaclass=ABCMeta):
    """Abstract base class for all XML descriptors.

    This class maintains a static index used for ordering all declared XML
    descriptors in an subclass. It is automatically incremented as needed.
    """

    _index = 0

    def __init__(self, name: str, namespace: str | None = None) -> None:
        """Initializes a new `XMLDescriptor`.
        When initializing a new XMLDescriptor object, the name (and possibly
        namespace) is used to construct an internal Qualified Name using
        Clark's notation.

        :param name: The name of the element to bind with.
        :param namespace: An optional namespace.
        """
        # Assign and increase the descriptor index.
        self._index = XMLDescriptor._index
        XMLDescriptor._index += 1

        self._name = name
        self._namespace = namespace

        if namespace:
            # Convert to Clark's notation.
            self._qname = util.to_clark(name, namespace)
        else:
            self._qname = name

    @abstractmethod
    def __get__(self, instance: Any, _owner: type | None = None) -> Any:
        pass

    @abstractmethod
    def __set__(self, instance: Any, value: Any) -> None:
        pass

    @abstractmethod
    def __delete__(self, instance: Any) -> None:
        pass


class ListingMeta(type):
    """A meta class for ordered XML Descriptor attributes.
    This meta class adds an extra property, `__listing__`, which includes all
    `XMLDescriptor` properties in their declared order.
    """

    def __new__(
        cls,
        name: str,
        bases: tuple[type, ...],
        class_dict: dict[str, Any],
    ) -> type:
        def is_member(member: Any) -> bool:
            """Checks if a member is an XMLDescriptor."""
            # Only return members that are instances of XMLDescriptor.
            result = isinstance(member, XMLDescriptor)
            return result

        # Create a new class.
        klass = type.__new__(cls, name, bases, class_dict)
        members = inspect.getmembers(klass, is_member)
        # Use setattr to add __listing__ attribute dynamically
        setattr(
            klass, "__listing__", sorted(members, key=lambda i: i[1]._index)
        )

        return klass


class XMLAttribute(XMLDescriptor, Generic[T]):
    """Bind an XML attribute to a typed Python value.

    This is a generic descriptor where T represents the type returned when
    accessing the attribute on an instance. The converter transforms between
    XML string values and Python type T.

    Example usage:
        class Element(XMLNode):
            # name: XMLAttribute[str] - accessing element.name returns str
            name = XMLAttribute("name", converter=StringConverter)
            # count: XMLAttribute[int] - accessing element.count returns int
            count = XMLAttribute("count", converter=IntegerConverter)
    """

    _converter: type[ConverterProtocol[T]]

    def __init__(
        self,
        name: str,
        namespace: str | None = None,
        converter: type[ConverterProtocol[T]] | None = None,
    ) -> None:
        """Initializes a new `XMLAttribute`.

        :param name: The name of the attribute to bind with.
        :param namespace: An optional namespace.
        :param converter: An optional data type converter.
        """
        super().__init__(name, namespace)

        # Use a StringConverter if None is given.
        if converter is None:
            # Default to StringConverter, cast needed for type checker
            self._converter = cast(type[ConverterProtocol[T]], StringConverter)
        else:
            self._converter = converter

    @overload
    def __get__(
        self, instance: None, owner: type | None = None
    ) -> "XMLAttribute[T]": ...

    @overload
    def __get__(
        self, instance: Any, owner: type | None = None
    ) -> T | None: ...

    def __get__(
        self, instance: Any, owner: type | None = None
    ) -> "XMLAttribute[T] | T | None":
        if instance is None:
            return self

        attribute = instance._element.get(self._qname)
        return self._converter.from_string(attribute)

    def __set__(self, instance: Any, value: T | None) -> None:
        instance._element.set(self._qname, self._converter.to_string(value))

    def __delete__(self, instance: Any) -> None:
        del instance._element.attrib[self._qname]


class XMLNode(metaclass=ListingMeta):
    """Base class for all binding nodes."""

    def __init__(self, element: ElementTree.Element | None = None) -> None:
        """Initializes a new `XMLNode`.
        If no base element is provided, the instance is instructed to create a
        new element (and possibly child elements).
        Args:
            element (Element): The root Element on which to bind.
        Raises:
            TypeError: If `element` is of the wrong type.
        """
        if element is None:
            element = self.create()
        elif not isinstance(element, ElementTree.Element):
            raise TypeError(
                "Expected {0:s}, got {1:s}".format(
                    ElementTree.__name__, element.__class__.__name__
                )
            )

        self._element: ElementTree.Element | None = element
        self._bindings: dict[str, Any] = {}

    @property
    def element(self) -> ElementTree.Element | None:
        """Get the backing XML element."""
        return self._element

    @staticmethod
    @abstractmethod
    def create() -> ElementTree.Element | None:
        """Create a new XML element for the node."""
        raise NotImplementedError()


class XMLElement(XMLDescriptor, Generic[T]):
    """Map an XML child element to a Python object instance.

    This is a generic descriptor where T represents the type returned when
    accessing the attribute on an instance. Typically T is an XMLNode
    subclass that wraps the child element.

    Example usage:
        class Parent(XMLNode):
            # child: XMLElement[Child] - accessing parent.child returns Child
            child = XMLElement("child", binder=Child)

    Type parameter T is inferred from the binder argument, which is a
    callable that takes an ElementTree.Element and returns T.

    The descriptor protocol (__get__/__set__/__delete__) is implemented
    with @overload to properly type:
    - Class access (Parent.child): Returns XMLElement[T] (the descriptor)
    - Instance access (parent.child): Returns T | None (bound value or None)
    """

    # The binder is a callable (typically a class constructor) that takes
    # an XML Element and returns an instance of type T.
    _binder: Callable[[ElementTree.Element], T] | None

    def __init__(
        self,
        name: str,
        binder: Callable[[ElementTree.Element], T] | None = None,
        namespace: str | None = None,
        required: bool = True,
        nillable: bool = False,
    ) -> None:
        """Initialize an XMLElement descriptor.

        :param name: The XML element name to bind to.
        :param binder: Callable that converts Element to T (usually a class).
        :param namespace: Optional XML namespace for the element.
        :param required: If True, deletion raises AttributeError.
        :param nillable: If True, xsi:nil="true" returns None.
        """
        super().__init__(name, namespace)

        self._binder = binder
        self._required = required
        self._nillable = nillable

    @property
    def nillable(self) -> bool:
        """Whether this element supports xsi:nil."""
        return self._nillable

    def index(self, instance: Any) -> int:
        """Returns the element index of this descriptor for a given class."""
        if not isinstance(type(instance), ListingMeta):
            # type(instance) returns type[Unknown] since instance is Any.
            # Cast to type for error message - we only need its string repr.
            instance_type: type = type(instance)  # type: ignore[assignment]
            raise TypeError(
                f"Expected type ListingMeta, got {instance_type!s}"
            )

        # Get the index of the descriptor.
        descriptors = [e[1] for e in instance.__listing__]
        attr_index = descriptors.index(self)

        # Find the first non-empty predecessor sibling element.
        for index in reversed(list(range(0, attr_index))):
            predecessor = descriptors[index]

            if predecessor._element is not None:
                attr_index = index
                break

        return attr_index

    # Overload 1: Class access (e.g., MyClass.attr) returns the descriptor.
    @overload
    def __get__(
        self, instance: None, owner: type | None = None
    ) -> "XMLElement[T]": ...

    # Overload 2: Instance access (e.g., obj.attr) returns T or None.
    @overload
    def __get__(
        self, instance: Any, owner: type | None = None
    ) -> T | None: ...

    def __get__(
        self, instance: Any, owner: type | None = None
    ) -> "XMLElement[T] | T | None":
        """Get the bound value from an instance.

        When accessed on the class, returns the descriptor itself.
        When accessed on an instance, returns:
        - The cached binder instance if previously accessed
        - A new binder instance wrapping the child element
        - None if the child element doesn't exist
        """
        if instance is None:
            # Class access - return the descriptor for introspection
            return self

        # Check for cached binder from previous access
        if hash(self) in instance._bindings:
            # Bindings dict stores T instances but is typed as dict[str, Any]
            # for flexibility. The binder ensures correct type at runtime.
            result = instance._bindings[hash(self)]
            return result  # type: ignore[no-any-return]

        # No previous binder found. Get the element, if it exists, and
        # instantiate a new one.
        element = instance._element.find(self._qname)

        if element is None:
            # No element exists. It must have been removed.
            return None

        # Create a new binder for the existing element.
        if self._binder is None:
            # When no binder is provided, return raw Element. This path is
            # used by XMLValue which overrides __get__ to handle conversion.
            return element  # type: ignore[return-value]

        binder = self._binder(element)
        instance._bindings[hash(self)] = binder

        return binder

    def __set__(self, instance: Any, value: Any) -> None:
        # If there is a previous value assigned, (try to) delete it first.
        if hash(self) in instance._bindings:
            del instance._bindings[hash(self)]

        if self._binder is None:
            # No binder - just store the value directly
            instance._bindings[hash(self)] = value
            return

        # If the value is None, set it to a new element. The binder is expected
        # to understand how to create a new, empty element.
        if value is None:
            # _binder is typically an XMLNode subclass with a create() method.
            # Using getattr since Callable type doesn't expose create().
            value = getattr(self._binder, "create")()

        # Create a new binder based on the specified element.
        binder = self._binder(value)
        instance._bindings[hash(self)] = binder

        # Add the element to the parent
        index = self.index(instance)
        instance._element.insert(index, value)

    def __delete__(self, instance: Any) -> None:
        """Deletes an element."""
        if self._required:
            raise AttributeError("Element is required, cannot delete.")
        elif hash(self) in instance._bindings:
            del instance._bindings[hash(self)]

        element = instance._element.find(self._qname)

        if element is not None:
            instance._element.remove(element)


class XMLElementList(XMLElement[T]):
    """Map a container element with repeated child elements to a list.

    This descriptor handles XML structures like:
        <items>
            <item>...</item>
            <item>...</item>
        </items>

    Generic type parameter T represents the type of items in the list.
    Each child element is wrapped using the binder to create T instances.

    Example usage:
        class Container(XMLNode):
            # items: XMLElementList[Item] - returns MutableSequence[Item]
            items = XMLElementList("items", child_name="item", binder=Item)
    """

    class List(MutableSequence[Any]):
        """Internal mutable list implementation.

        Wraps the XML element children and provides list-like access.
        Modifications to the list are reflected in the XML structure.

        Note: Uses Any instead of T to avoid TypeVar scope issues with
        nested classes in Python's type system. Type safety for users is
        provided by the outer XMLElementList descriptor's return type.
        """

        def __init__(
            self,
            parent: "XMLElementList[Any]",
            element: ElementTree.Element,
            binder: Callable[[ElementTree.Element], Any],
            qname: str,
        ) -> None:
            super().__init__()

            self._list: list[Any] = list()
            self._parent = parent
            self._element = element
            self._binder = binder
            self._qname = qname

            children = self._element.findall(qname)

            for child in children:
                self._list.append(self._binder(child))

        def __len__(self) -> int:
            return len(self._list)

        # MutableSequence expects __getitem__, __delitem__, __setitem__ to
        # accept int | slice, but this implementation only supports int keys.
        # Using type: ignore[override] to document this intentional limitation.
        def __getitem__(self, key: int) -> Any:  # type: ignore[override]
            return self._list[key]

        def __delitem__(self, key: int) -> None:  # type: ignore[override]
            item = self._list[key]

            element: ElementTree.Element
            if isinstance(item, XMLNode):
                # element is set in XMLNode.__init__, so it's never None here
                assert item.element is not None
                element = item.element
            else:
                # Item is not an XMLNode, assume it's an Element directly
                element = item

            self._element.remove(element)

            del self._list[key]

            if self._parent.nillable:
                if not self._list:
                    self._element.set(ATTR_NIL, "true")
                    self._element.text = None

        def __setitem__(  # type: ignore[override]
            self, key: int, value: Any
        ) -> None:
            # If there is a previous value assigned, remove it.
            old = self._list[key]

            if old is not None:
                # Access _element attribute - value is expected to be XMLNode
                old_elem = getattr(old, "_element", None)
                if old_elem is not None:
                    self._element.remove(old_elem)

            # Access _element attribute on value
            value_elem = getattr(value, "_element", None)
            if value_elem is not None:
                self._element.insert(key, value_elem)
            self._list[key] = value

        def insert(self, index: int, value: Any) -> None:
            # Access _element attribute - value is expected to be XMLNode
            value_elem = getattr(value, "_element", None)
            if value_elem is not None:
                self._element.insert(index, value_elem)
            self._list.insert(index, value)

            # Check if nillable.
            if self._parent.nillable:
                if ATTR_NIL in self._element.attrib:
                    del self._element.attrib[ATTR_NIL]

        def __str__(self) -> str:
            return str(self._list)

    _child_binder: Callable[[ElementTree.Element], T]

    def __init__(
        self,
        name: str,
        child_name: str,
        binder: Callable[[ElementTree.Element], T],
        namespace: str | None = None,
        child_namespace: str | None = None,
        required: bool = True,
        nillable: bool = False,
    ) -> None:
        super().__init__(
            name=name,
            binder=None,
            namespace=namespace,
            required=required,
            nillable=nillable,
        )

        self._child_binder = binder
        self._child_name = child_name
        self._child_namespace = child_namespace

        if child_namespace:
            # Convert to Clark's notation.
            self._child_qname = util.to_clark(child_name, child_namespace)
        else:
            self._child_qname = child_name

    @overload
    def __get__(
        self, instance: None, owner: type | None = None
    ) -> "XMLElementList[T]": ...

    @overload
    def __get__(
        self, instance: Any, owner: type | None = None
    ) -> "XMLElementList.List | None": ...

    # Return type differs from XMLElement.__get__ - returns List instead of T.
    # This is intentional as XMLElementList wraps elements in a List container.
    def __get__(  # type: ignore[override]
        self, instance: Any, owner: type | None = None
    ) -> "XMLElementList[T] | XMLElementList.List | None":
        # Type is unknown here because parent's T is unbound; we cast after
        # narrowing checks below
        result = super().__get__(instance, owner)  # type: ignore[reportUnknownVariableType]  # noqa: E501  # noqa: E501

        if result is None:
            # Element doesn't exist, return None
            return None
        elif result is self:
            return self

        # After the above checks, result is the raw Element (since binder=None
        # in __init__) or an already-wrapped List from the bindings cache.
        if isinstance(result, XMLElementList.List):
            return result

        # At this point, result is an ElementTree.Element
        element = cast(ElementTree.Element, result)

        # Check if nillable.
        if self._nillable:
            if ATTR_NIL in element.attrib:
                if element.get(ATTR_NIL) == "true":
                    # Since nil=true, return None.
                    return None

        binder = XMLElementList.List(
            parent=self,
            element=element,
            binder=self._child_binder,
            qname=self._child_qname,
        )

        instance._bindings[hash(self)] = binder

        return binder


class XMLValue(XMLElement[T]):
    """Map an element's text content to a typed Python value.

    Unlike XMLElement which wraps child elements in binder objects,
    XMLValue extracts and converts the text content of an element.

    Generic type parameter T represents the Python type produced by the
    converter (e.g., str for StringConverter, int for IntegerConverter).

    Example usage:
        class Person(XMLNode):
            # name: XMLValue[str] - accessing person.name returns str
            name = XMLValue("name", converter=StringConverter)
            # age: XMLValue[int] - accessing person.age returns int
            age = XMLValue("age", converter=IntegerConverter)

    The converter protocol defines from_string/to_string methods that
    handle the conversion between XML text and Python types.
    """

    # The converter class that transforms between XML strings and type T
    _converter: type[ConverterProtocol[T]]

    def __init__(
        self,
        name: str,
        converter: type[ConverterProtocol[T]],
        namespace: str | None = None,
        required: bool = True,
        nillable: bool = False,
    ) -> None:
        """Initialize an XMLValue descriptor.

        :param name: The XML element name containing the text value.
        :param converter: Converter class for string<->T transformation.
        :param namespace: Optional XML namespace for the element.
        :param required: If True, setting None raises ValueError.
        :param nillable: If True, None sets xsi:nil="true" on element.
        """
        super().__init__(
            name,
            binder=None,  # XMLValue doesn't use a binder - it uses converter
            namespace=namespace,
            required=required,
            nillable=nillable,
        )

        self._converter = converter

    @overload
    def __get__(
        self, instance: None, owner: type | None = None
    ) -> "XMLValue[T]": ...

    @overload
    def __get__(
        self, instance: Any, owner: type | None = None
    ) -> T | None: ...

    def __get__(
        self, instance: Any, owner: type | None = None
    ) -> "XMLValue[T] | T | None":
        # Type is unknown here because parent's T is unbound; we cast after
        # narrowing checks below
        result = super().__get__(instance, owner)  # type: ignore[reportUnknownVariableType]  # noqa: E501

        if result is None:
            return None
        elif result is self:
            return self

        # After the above checks, result is the raw Element (since binder=None
        # in __init__).
        element = cast(ElementTree.Element, result)

        # Check if nillable.
        if self._nillable:
            if ATTR_NIL in element.attrib:
                if element.get(ATTR_NIL) == "true":
                    # Since nil=true, return None regardless of any text.
                    return None

        return self._converter.from_string(element.text)

    def __set__(self, instance: Any, value: T | None) -> None:
        # Type is unknown here because parent's T is unbound; we cast below
        result = super().__get__(instance, None)  # type: ignore[reportUnknownVariableType]  # noqa: E501

        if result is None:
            element = ElementTree.Element(self._qname)
            super().__set__(instance, element)
        else:
            element = cast(ElementTree.Element, result)

        if self._nillable:
            attr = "{{{0:s}}}{1:s}".format(NS_XSI, "nil")

            if value is None:
                element.attrib[attr] = "true"
            else:
                if attr in element.attrib:
                    del element.attrib[attr]
        elif value is None:
            raise ValueError("Element not nillable.")

        element.text = self._converter.to_string(value)


class XMLValueList(XMLElement[T]):
    """Map a container element with repeated value elements to a list.

    Similar to XMLElementList, but for simple values instead of complex
    elements. Each child element's text content is converted to type T.

    Example XML:
        <tags>
            <tag>python</tag>
            <tag>xml</tag>
        </tags>

    Example usage:
        class Article(XMLNode):
            # tags: XMLValueList[str] - returns MutableSequence[str]
            tags = XMLValueList("tags", child_name="tag",
                                converter=StringConverter)

    Generic type parameter T represents the Python type produced by the
    converter (e.g., str, int, bool).
    """

    class List(MutableSequence[Any]):
        """Internal mutable list implementation for value elements.

        Wraps the XML child elements and provides list-like access.
        Each element's text content is converted using the converter.

        Note: Uses Any instead of T to avoid TypeVar scope issues with
        nested classes in Python's type system. Type safety for users is
        provided by the outer XMLValueList descriptor's return type.
        """

        def __init__(
            self,
            parent: "XMLValueList[Any]",
            element: ElementTree.Element,
            converter: type[ConverterProtocol[Any]],
            qname: str,
        ) -> None:
            super().__init__()

            self._list: list[ElementTree.Element] = list()
            self._parent = parent
            self._element = element
            self._converter = converter
            self._qname = qname

            children = self._element.findall(qname)

            for child in children:
                self._list.append(child)

        def __len__(self) -> int:
            return len(self._list)

        # MutableSequence expects __getitem__, __delitem__, __setitem__ to
        # accept int | slice, but this implementation only supports int keys.
        # Using type: ignore[override] to document this intentional limitation.
        def __getitem__(self, key: int) -> Any:  # type: ignore[override]
            return self._converter.from_string(self._list[key].text)

        def __delitem__(self, key: int) -> None:  # type: ignore[override]
            item = self._list[key]
            self._element.remove(item)
            del self._list[key]

            if self._parent.nillable:
                if not self._list:
                    self._element.set(ATTR_NIL, "true")
                    self._element.text = None

        def __setitem__(  # type: ignore[override]
            self, key: int, value: Any
        ) -> None:
            self._list[key].text = self._converter.to_string(value)

        def insert(self, index: int, value: Any) -> None:
            element = ElementTree.Element(self._qname)
            element.text = self._converter.to_string(value)

            self._element.insert(index, element)
            self._list.insert(index, element)

            # Check if nillable.
            if self._parent.nillable:
                if ATTR_NIL in self._element.attrib:
                    del self._element.attrib[ATTR_NIL]

        def __str__(self) -> str:
            return str(self._list)

    _converter: type[ConverterProtocol[T]]

    def __init__(
        self,
        name: str,
        child_name: str,
        converter: type[ConverterProtocol[T]],
        namespace: str | None = None,
        child_namespace: str | None = None,
        required: bool = True,
        nillable: bool = False,
    ) -> None:
        super().__init__(
            name=name,
            binder=None,
            namespace=namespace,
            required=required,
            nillable=nillable,
        )

        self._converter = converter
        self._child_name = child_name
        self._child_namespace = child_namespace

        if child_namespace:
            # Convert to Clark's notation.
            self._child_qname = util.to_clark(child_name, child_namespace)
        else:
            self._child_qname = child_name

    @overload
    def __get__(
        self, instance: None, owner: type | None = None
    ) -> "XMLValueList[T]": ...

    @overload
    def __get__(
        self, instance: Any, owner: type | None = None
    ) -> "XMLValueList.List | None": ...

    # Return type differs from XMLElement.__get__ - returns List instead of T.
    # This is intentional as XMLValueList wraps values in a List container.
    def __get__(  # type: ignore[override]
        self, instance: Any, owner: type | None = None
    ) -> "XMLValueList[T] | XMLValueList.List | None":
        # Type is unknown here because parent's T is unbound; we cast after
        # narrowing checks below
        result = super().__get__(instance, owner)  # type: ignore[reportUnknownVariableType]  # noqa: E501

        if result is None:
            return None
        elif result is self:
            return self

        # After the above checks, result is the raw Element (since binder=None
        # in __init__) or an already-wrapped List from the bindings cache.
        if isinstance(result, XMLValueList.List):
            return result

        # At this point, result is an ElementTree.Element
        element = cast(ElementTree.Element, result)

        binder = XMLValueList.List(
            parent=self,
            element=element,
            converter=self._converter,
            qname=self._child_qname,
        )

        instance._bindings[hash(self)] = binder

        return binder
