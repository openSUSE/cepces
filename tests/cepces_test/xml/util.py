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
import unittest


class TestToClarkNotation(unittest.TestCase):
    def testName(self):
        """Name should not be changed when namespace is None"""
        name = "TestName"

        self.assertEqual(util.to_clark(name), name)

    def testNameAndNamespace(self):
        """Result should follow Clarks's notation"""
        name = "TestName"
        namespace = "TestNameSpace"

        self.assertEqual(
            util.to_clark(name, namespace),
            "{{{1:s}}}{0:s}".format(name, namespace),
        )

    def testNamespace(self):
        """Only specifying the namespace should fail"""
        namespace = "TestNameSpace"

        with self.assertRaises(TypeError):
            util.to_clark(None, namespace)


class TestFromClarkNotation(unittest.TestCase):
    def testOnlyName(self):
        """Input should be returned unaltered"""
        name = "TestName"
        rname, rnamespace = util.from_clark(name)

        self.assertEqual(rname, name)
        self.assertEqual(rnamespace, None)

    def testNameAndNamespace(self):
        """(name, namsepace) tuple should be returned"""
        name = "TestName"
        namespace = "TestNamespace"

        clarke = util.to_clark(name, namespace)
        rname, rnamespace = util.from_clark(clarke)

        self.assertEqual(name, rname)
        self.assertEqual(namespace, rnamespace)

    def testOnlyNamespace(self):
        """Having only a namespace should fail"""
        string = "{TestNamespace}"

        with self.assertRaises(ValueError):
            util.from_clark(string)
