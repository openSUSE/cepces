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
import ctypes

# Try to load the Kerberos5 library dynamically. Naïvely try to load everything
# in the list until successful.
_shlib = None
_libs = [
    'libgssapi_krb5.so',
    'libgssapi_krb5.so.2',
    'libgssapi_krb5.dylib',
]

for lib in _libs:
    if _shlib is not None:
        break
    else:
        try:
            _shlib = ctypes.CDLL(lib)
        except:
            pass

# If no library was found, fail.
if _shlib is None:
    raise RuntimeError("Could not load any Kerberos library.")
