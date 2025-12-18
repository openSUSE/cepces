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
"""Module containing XML bindings."""
from collections.abc import MutableSequence
from xml.etree import ElementTree
import inspect
from abc import ABCMeta, abstractmethod
from cepces.xml import ATTR_NIL, NS_XSI, util
from cepces.xml.converter import StringConverter


class XMLDescriptor(metaclass=ABCMeta):
    """Abstract base class for all XML descriptors.

    This class maintains a static index used for ordering all declared XML
    descriptors in an subclass. It is automatically incremented as needed.
    """

    _index = 0

    def __init__(self, name, namespace=None):
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
    def __get__(self, instance, _owner=None):
        pass

    @abstractmethod
    def __set__(self, instance, value):
        pass

    @abstractmethod
    def __delete__(self, instance):
        pass


class ListingMeta(type):
    """A meta class for ordered XML Descriptor attributes.
    This meta class adds an extra property, `__listing__`, which includes all
    `XMLDescriptor` properties in their declared order.
    """

    def __new__(cls, name, bases, class_dict):
        def is_member(member):
            """Checks if a member is an XMLDescriptor."""
            # Only return members that are instances of XMLDescriptor.
            result = isinstance(member, XMLDescriptor)
            return result

        # Create a new class.
        klass = type.__new__(cls, name, bases, class_dict)
        members = inspect.getmembers(klass, is_member)
        klass.__listing__ = sorted(members, key=lambda i: i[1]._index)

        return klass


class XMLAttribute(XMLDescriptor):
    """This class binds to an attribute of an element."""

    def __init__(self, name, namespace=None, converter=None):
        """Initializes a new `XMLAttribute`.

        :param name: The name of the element to bind with.
        :param namespace: An optional namespace.
        :param converter: An optional data type converter.
        """
        super().__init__(name, namespace)

        # Use a StringConverter if None is given.
        if converter is None:
            converter = StringConverter

        self._converter = converter

    def __get__(self, instance, _owner=None):
        attribute = instance._element.get(self._qname)

        return self._converter.from_string(attribute)

    def __set__(self, instance, value):
        instance._element.set(self._qname, self._converter.to_string(value))

    def __delete__(self, instance):
        del instance._element.attrib[self._qname]


class XMLNode(metaclass=ListingMeta):
    """Base class for all binding nodes."""

    def __init__(self, element=None):
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

        self._element = element
        self._bindings = {}

    @property
    def element(self):
        """Get the backing XML element."""
        return self._element

    @staticmethod
    @abstractmethod
    def create():
        """Create a new XML element for the node."""
        raise NotImplementedError()


class XMLElement(XMLDescriptor):
    """Map an element to an XMLNode instance."""

    def __init__(
        self, name, binder=None, namespace=None, required=True, nillable=False
    ):
        super().__init__(name, namespace)

        if binder is None:

            def func(value):
                """Simple pass-through function."""
                return value

            binder = func

        self._binder = binder
        self._required = required
        self._nillable = nillable

    def index(self, instance):
        """Returns the element index of this descriptor for a given class."""
        if not isinstance(type(instance), ListingMeta):
            raise TypeError(
                "Expected type ListingMeta, got {0:s}".format(
                    str(type(instance))
                )
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

    def __get__(self, instance, _owner=None):
        if instance is None:
            return self

        # Get any previous binder.
        if hash(self) in instance._bindings:
            return instance._bindings[hash(self)]

        # No previous binder found. Get the element, if it exists, and
        # instantiate a new one.
        element = instance._element.find(self._qname)

        if element is None:
            # No element exists. It must have been removed.
            return None

        # Create a new binder for the existing element.
        binder = self._binder(element)
        instance._bindings[hash(self)] = binder

        return binder

    def __set__(self, instance, value):
        # If there is a previous value assigned, (try to) delete it first.
        if hash(self) in instance._bindings:
            del instance._bindings[hash(self)]

        # If the value is None, set it to a new element. The binder is expected
        # to understand how to create a new, empty element.
        if value is None:
            value = self._binder.create()

        # Create a new binder based on the specified element.
        binder = self._binder(value)
        instance._bindings[hash(self)] = binder

        # Add the element to the parent
        index = self.index(instance)
        instance._element.insert(index, value)

    def __delete__(self, instance):
        """Deletes an element."""
        if self._required:
            raise AttributeError("Element is required, cannot delete.")
        elif hash(self) in instance._bindings:
            del instance._bindings[hash(self)]

        element = instance._element.find(self._qname)

        if element is not None:
            instance._element.remove(element)


class XMLElementList(XMLElement):
    """XML Element List"""

    class List(MutableSequence):
        """Internal list."""

        def __init__(self, parent, element, binder, qname):
            super().__init__()

            self._list = list()
            self._parent = parent
            self._element = element
            self._binder = binder
            self._qname = qname

            children = self._element.findall(qname)

            for child in children:
                self._list.append(self._binder(child))

        def __len__(self):
            return len(self._list)

        def __getitem__(self, key):
            return self._list[key]

        def __delitem__(self, key):
            item = self._list[key]

            if isinstance(item, XMLNode):
                item = item._element

            self._element.remove(item)

            del self._list[key]

            if self._parent._nillable:
                if not self._list:
                    self._element.set(ATTR_NIL, "true")
                    self._element.text = None

        def __setitem__(self, key, value):
            # Value has to be of the same type as the binder.
            if not isinstance(value, self._binder):
                raise TypeError(
                    "Expected value of {0:s}".format(str(type(self._binder)))
                )

            # If there is a previous value assigned, remove it.
            old = self._list[key]

            if old is not None:
                self._element.remove(old._element)

            self._element.insert(key, value._element)
            self._list[key] = value

        # pylint: disable=arguments-differ
        def insert(self, key, value):
            self._element.insert(key, value._element)
            self._list.insert(key, value)

            # Check if nillable.
            if self._parent._nillable:
                if ATTR_NIL in self._element.attrib:
                    del self._element.attrib[ATTR_NIL]

        def __str__(self):
            return str(self._list)

    def __init__(
        self,
        name,
        child_name,
        binder,
        namespace=None,
        child_namespace=None,
        required=True,
        nillable=False,
    ):
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

    def __get__(self, instance, _owner=None):
        binder = super().__get__(instance, _owner)

        if binder is None:
            # Element doesn't exist, return None
            return None
        elif binder is self:
            return binder

        # Check if nillable.
        if self._nillable:
            if hasattr(binder, "attrib") and ATTR_NIL in binder.attrib:
                if binder.get(ATTR_NIL) == "true":
                    # Since nil=true, return None.
                    return None

        if not isinstance(binder, XMLElementList.List):
            binder = XMLElementList.List(
                parent=self,
                element=binder,
                binder=self._child_binder,
                qname=self._child_qname,
            )

            instance._bindings[hash(self)] = binder

        return binder


class XMLValue(XMLElement):
    """XML Value"""

    def __init__(
        self, name, converter, namespace=None, required=True, nillable=False
    ):
        super().__init__(
            name,
            binder=None,
            namespace=namespace,
            required=required,
            nillable=nillable,
        )

        self._converter = converter

    def __get__(self, instance, _owner=None):
        element = super().__get__(instance, _owner)

        if element is None:
            return None
        elif element is self:
            return self

        # Check if nillable.
        if self._nillable:
            if hasattr(element, "attrib") and ATTR_NIL in element.attrib:
                if element.get(ATTR_NIL) == "true":
                    # Since nil=true, return None regardless of any text.
                    return None

        if hasattr(element, "text"):
            return self._converter.from_string(element.text)

        return self._converter.from_string("")

    def __set__(self, instance, value):
        element = super().__get__(instance, None)

        if element is None:
            element = ElementTree.Element(self._qname)
            super().__set__(instance, element)

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


class XMLValueList(XMLElement):
    """XML Value List"""

    class List(MutableSequence):
        """Internal list"""

        def __init__(self, parent, element, converter, qname):
            super().__init__()

            self._list = list()
            self._parent = parent
            self._element = element
            self._converter = converter
            self._qname = qname

            children = self._element.findall(qname)

            for child in children:
                self._list.append(child)

        def __len__(self):
            return len(self._list)

        def __getitem__(self, key):
            return self._converter.from_string(self._list[key].text)

        def __delitem__(self, key):
            item = self._list[key]
            self._element.remove(item)
            del self._list[key]

            if self._parent._nillable:
                if not self._list:
                    self._element.set(ATTR_NIL, "true")
                    self._element.text = None

        def __setitem__(self, key, value):
            self._list[key].text = self._converter.to_string(value)

        # pylint: disable=arguments-differ
        def insert(self, key, value):
            element = ElementTree.Element(self._qname)
            element.text = self._converter.to_string(value)

            self._element.insert(key, element)
            self._list.insert(key, element)

            # Check if nillable.
            if self._parent._nillable:
                if ATTR_NIL in self._element.attrib:
                    del self._element.attrib[ATTR_NIL]

        def __str__(self):
            return str(self._list)

    def __init__(
        self,
        name,
        child_name,
        converter,
        namespace=None,
        child_namespace=None,
        required=True,
        nillable=False,
    ):
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

    def __get__(self, instance, _owner=None):
        binder = super().__get__(instance, _owner)

        if binder is self:
            return binder
        elif not isinstance(binder, XMLValueList.List):
            binder = XMLValueList.List(
                parent=self,
                element=binder,
                converter=self._converter,
                qname=self._child_qname,
            )

            instance._bindings[hash(self)] = binder

            return binder
        return None
