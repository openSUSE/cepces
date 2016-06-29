# -*- coding: utf-8 -*-
#
# This file is part of cepces.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 2 of the GNU General
# Public License as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the Free
# Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301, USA
#
from cepces.xml import util
import unittest


class TestToClarkNotation(unittest.TestCase):
    def testName(self):
        '''Name should not be changed when namespace is None'''
        name = 'TestName'

        self.assertEqual(util.to_clarke(name), name)

    def testNameAndNamespace(self):
        '''Result should follow Clarks's notation'''
        name = 'TestName'
        namespace = 'TestNameSpace'

        self.assertEqual(
            util.to_clarke(name, namespace),
            '{{{1:s}}}{0:s}'.format(name, namespace)
        )

    def testNamespace(self):
        '''Only specifying the namespace should fail'''
        namespace = 'TestNameSpace'

        with self.assertRaises(TypeError):
            util.to_clarke(None, namespace)


class TestFromClarkNotation(unittest.TestCase):
    def testOnlyName(self):
        '''Input should be returned unaltered'''
        name = 'TestName'
        rname, rnamespace = util.from_clarke(name)

        self.assertEqual(rname, name)
        self.assertEqual(rnamespace, None)

    def testNameAndNamespace(self):
        '''(name, namsepace) tuple should be returned'''
        name = 'TestName'
        namespace = 'TestNamespace'

        clarke = util.to_clarke(name, namespace)
        rname, rnamespace = util.from_clarke(clarke)

        self.assertEqual(name, rname)
        self.assertEqual(namespace, rnamespace)

    def testOnlyNamespace(self):
        '''Having only a namespace should fail'''
        string = '{TestNamespace}'

        with self.assertRaises(ValueError):
            util.from_clarke(string)
