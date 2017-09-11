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
from cepces import __title__, __version__
import unittest
import cepces.certmonger.operation as CertmongerOperations
import io


class TestGetDefaultTemplate(unittest.TestCase):
    """Tests the GetDefaultTemplate operation"""

    def testCall(self):
        out = io.StringIO()
        operation = CertmongerOperations.GetDefaultTemplate(out=out)
        operation()

        self.assertEqual(out.getvalue(), '')


class TestIdentify(unittest.TestCase):
    """Tests the Identity operation"""

    def testCall(self):
        out = io.StringIO()
        operation = CertmongerOperations.Identify(out=out)
        operation()

        self.assertEqual(
            out.getvalue(),
            '{} {}\n'.format(__title__, __version__),
        )
