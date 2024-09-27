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
"""Package for very rudimentary SOAP  handling."""
from xml.etree.ElementTree import QName

NS_SOAP = 'http://www.w3.org/2003/05/soap-envelope'
NS_ADDRESSING = 'http://www.w3.org/2005/08/addressing'
NS_WSSE = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd'

# ACTION_FAULT = 'http://www.w3.org/2005/08/addressing/fault'
QNAME_FAULT = QName('http://www.w3.org/2003/05/soap-envelope', 'Fault')
