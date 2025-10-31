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
import cepces.certmonger.operation as CertmongerOperations
import io


def test_get_default_template_call():
    """Tests the GetDefaultTemplate operation"""
    out = io.StringIO()
    operation = CertmongerOperations.GetDefaultTemplate(None, out=out)
    operation()

    assert out.getvalue() == ""


def test_identify_call():
    """Tests the Identity operation"""
    out = io.StringIO()
    operation = CertmongerOperations.Identify(None, out=out)
    operation()

    assert out.getvalue() == "{} {}\n".format(__title__, __version__)
