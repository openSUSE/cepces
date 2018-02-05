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
"""This package contains WSTEP related logic."""

NS_WST = 'http://docs.oasis-open.org/ws-sx/ws-trust/200512'
NS_WST_SECEXT = 'http://docs.oasis-open.org/wss/2004/01/' \
                'oasis-200401-wss-wssecurity-secext-1.0.xsd'
NS_ENROLLMENT = 'http://schemas.microsoft.com/windows/pki/2009/01/enrollment'

TOKEN_TYPE = 'http://docs.oasis-open.org/wss/2004/01/' \
             'oasis-200401-wss-x509-token-profile-1.0#X509v3'
ISSUE_REQUEST_TYPE = 'http://docs.oasis-open.org/ws-sx/ws-trust/200512/Issue'
QUERY_REQUEST_TYPE = 'http://schemas.microsoft.com/windows/pki/2009/01/' \
                     'enrollment/QueryTokenStatus'
VALUE_TYPE = 'http://schemas.microsoft.com/windows/pki/2009/01/' \
             'enrollment#PKCS10'
ENCODING_TYPE = 'http://docs.oasis-open.org/wss/2004/01/' \
                'oasis-200401-wss-wssecurity-secext-1.0.xsd#base64binary'
