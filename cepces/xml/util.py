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
import re


def to_clark(name, namespace=None):
    """Returns an element name in Clark's Notation."""
    if namespace:
        return '{{{1:s}}}{0:s}'.format(name, namespace)
    else:
        return str(name)


def from_clark(string):
    """Returns a (name, namespace) tuple from an element name following Clark's
    notation.

    Note that the URI is not checked whether it is well-formed or not.

    Raises ValueError on malformed input.
    """
    match = re.search('^(?:{(?P<namespace>.+)})?(?P<name>[^{}]+)$', string)

    if not match:
        raise ValueError("Invalid input, expected Clark's notation")

    name, namespace = match.group('name', 'namespace')

    return name, namespace
