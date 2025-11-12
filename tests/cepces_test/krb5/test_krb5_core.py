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
"""Tests for cepces.krb5.core module."""
import re
from cepces.krb5.core import get_default_keytab_name, NAME_EX


class TestGetDefaultKeytabNameFunction:
    """Tests for the standalone get_default_keytab_name function."""

    def test_function_returns_string(self):
        """Test that get_default_keytab_name function returns a string."""
        keytab_name = get_default_keytab_name()
        assert isinstance(keytab_name, str)

    def test_function_returns_non_empty(self):
        """Test function returns a non-empty string."""
        keytab_name = get_default_keytab_name()
        assert len(keytab_name) > 0

    def test_function_format(self):
        """Test function returns properly formatted name."""
        keytab_name = get_default_keytab_name()
        match = re.match(NAME_EX, keytab_name)
        assert match is not None
        assert match.group("residual") is not None

    def test_function_consistent(self):
        """Test function returns consistent results."""
        keytab_name1 = get_default_keytab_name()
        keytab_name2 = get_default_keytab_name()
        assert keytab_name1 == keytab_name2
