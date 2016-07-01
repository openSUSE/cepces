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
from cepces.xml import util
from xml.etree import ElementTree
import inspect
from abc import abstractmethod


class XMLDescriptor(object):
    """Base class for all XML descriptors.

    This class maintains a static index used for ordering all declared XML
    descriptors in an subclass. It is automatically incremented as needed.
    """
    _index = 0

    def __init__(self, name, namespace=None):
        """Initializes a new `XMLDescriptor`.

        When initializing a new XMLDescriptor object, the name (and possibly
        namespace) is used to construct an internal Qualified Name using
        Clark's notation.

        Args:
            name (str): The name of the element to bind with.
            namespace (str): An optional namespace.
        """
        # Increase the descriptor index.
        self._index = XMLDescriptor._index
        XMLDescriptor._index += 1

        self._name = name
        self._namespace = namespace

        if namespace:
            # Convert to Clark's notation.
            self._qname = util.to_clark(name, namespace)
        else:
            self._qname = name


class ListingMeta(type):
    """A meta class for ordered XML Descriptor attributes.

    This meta class adds an extra property, `__listing__`, which includes all
    `XMLDescriptor` properties in their declared order.
    """

    def __new__(cls, name, bases, class_dict):
        def is_member(member):
            # Only return members that are instances of XMLDescriptor.
            result = isinstance(member, XMLDescriptor)
            return result

        # Create a new class.
        klass = type.__new__(cls, name, bases, class_dict)
        members = inspect.getmembers(klass, is_member)
        klass.__listing__ = sorted(members, key=lambda i: i[1]._index)

        return klass


class XMLNode(metaclass=ListingMeta):
    """Base class for all binding nodes."""

    def __init__(self, element=None):
        """Initializes a new `BindingNode`.

        If no base element is provided, the instance is instructed to create a
        new element (and possibly child elements).

        Args:
            element (Element): The root Element on which to bind.

        Raises:
            TypeError: If `element` is of the wrong type.
        """
        # ElementTree.Element is a class in 2.7 and a function in 2.6.
        # Calling ElementTree.Element yields the following in:
        # * 2.6: <class xml.etree.ElementTree._ElementInterface at [addr]>
        # * 2.7: <class 'xml.etree.ElementTree.Element'>
        if element is None:
            element = self.create()
        elif not isinstance(element, ElementTree.Element):
            raise TypeError('Expected {0:s}, got {1:s}'.format(
                ElementTree.__name__,
                element.__class__.__name__))

        self._element = element
        self._bindings = {}

    @staticmethod
    @abstractmethod
    def create():
        raise NotImplementedError()
