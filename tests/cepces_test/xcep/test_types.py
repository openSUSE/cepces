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
# import pytest
from cepces.xcep.types import RequestFilter
from xml.etree.ElementTree import QName
from cepces.xcep import NS_CEP
from xml.etree.ElementTree import tostring


# @pytest.mark.xfail(reason="test_RequestFilter_message_types not implemented yet")
def test_RequestFilter_message_types():
    # ensure that clientVersion is a string of values xxx
    # ensur that serverVersion is a string of values xxx
    element = RequestFilter.create()
    print(tostring(element, encoding="unicode"))

    # token = element.get(QName(NS_CEP, "requestFilter"))

    client_version = element.find(f"{{{NS_CEP}}}clientVersion").text
    server_version = element.find(f"{{{NS_CEP}}}serverVersion").text
    assert client_version is not None, "clientVersion should not be None"
    assert server_version is not None, "serverVersion should not be None"
    print(client_version)

    assert isinstance(client_version, str)
    assert isinstance(server_version, str)

    assert (
        client_version == "6"
    ), f"client_version should be 6, got {client_version}"

    assert (
        server_version == "0"
    ), f"server_version should be 0, got {server_version}"
