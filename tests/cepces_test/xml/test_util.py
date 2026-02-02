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
import pytest


def test_to_clark_name() -> None:
    """Name should not be changed when namespace is None"""
    name = "TestName"
    assert util.to_clark(name) == name


def test_to_clark_name_and_namespace() -> None:
    """Result should follow Clarks's notation"""
    name = "TestName"
    namespace = "TestNameSpace"

    assert util.to_clark(name, namespace) == "{{{1:s}}}{0:s}".format(
        name, namespace
    )


def test_to_clark_namespace_only() -> None:
    """Only specifying the namespace should fail"""
    namespace = "TestNameSpace"

    with pytest.raises(TypeError):
        # Intentionally passing None to test error handling
        util.to_clark(None, namespace)  # type: ignore[arg-type]


def test_from_clark_only_name() -> None:
    """Input should be returned unaltered"""
    name = "TestName"
    rname, rnamespace = util.from_clark(name)

    assert rname == name
    assert rnamespace is None


def test_from_clark_name_and_namespace() -> None:
    """(name, namsepace) tuple should be returned"""
    name = "TestName"
    namespace = "TestNamespace"

    clarke = util.to_clark(name, namespace)
    rname, rnamespace = util.from_clark(clarke)

    assert name == rname
    assert namespace == rnamespace


def test_from_clark_only_namespace() -> None:
    """Having only a namespace should fail"""
    string = "{TestNamespace}"

    with pytest.raises(ValueError):
        util.from_clark(string)
