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
"""Tests for XCEP types."""

from cepces.xcep.types import (
    RequestFilter,
    GetPolicies,
    XCEP_CLIENT_VERSION,
    XCEP_SERVER_VERSION,
)
from cepces.xcep import NS_CEP


class TestRequestFilterCreate:
    """Tests for RequestFilter.create() method."""

    def test_creates_request_filter_element(self):
        """create() should return a requestFilter element."""
        element = RequestFilter.create()

        assert element.tag == f"{{{NS_CEP}}}requestFilter"

    def test_has_policy_oids_element(self):
        """requestFilter should contain policyOIDs element."""
        element = RequestFilter.create()

        policy_oids = element.find(f"{{{NS_CEP}}}policyOIDs")
        assert policy_oids is not None, "policyOIDs element not found"

    def test_policy_oids_is_nil(self):
        """policyOIDs should have xsi:nil='true' attribute."""
        element = RequestFilter.create()

        policy_oids = element.find(f"{{{NS_CEP}}}policyOIDs")
        assert policy_oids is not None

        nil_attr = policy_oids.get(
            "{http://www.w3.org/2001/XMLSchema-instance}nil"
        )
        assert nil_attr == "true", "policyOIDs should be nil"

    def test_has_client_version_element(self):
        """requestFilter should contain clientVersion element."""
        element = RequestFilter.create()

        client_version = element.find(f"{{{NS_CEP}}}clientVersion")
        assert client_version is not None, "clientVersion element not found"

    def test_client_version_value(self):
        """clientVersion should be set to XCEP_CLIENT_VERSION."""
        element = RequestFilter.create()

        client_version = element.find(f"{{{NS_CEP}}}clientVersion")
        assert client_version is not None
        assert client_version.text == str(XCEP_CLIENT_VERSION)

    def test_client_version_not_nil(self):
        """clientVersion should NOT have xsi:nil attribute."""
        element = RequestFilter.create()

        client_version = element.find(f"{{{NS_CEP}}}clientVersion")
        assert client_version is not None

        nil_attr = client_version.get(
            "{http://www.w3.org/2001/XMLSchema-instance}nil"
        )
        assert nil_attr is None, "clientVersion should not be nil"

    def test_has_server_version_element(self):
        """requestFilter should contain serverVersion element."""
        element = RequestFilter.create()

        server_version = element.find(f"{{{NS_CEP}}}serverVersion")
        assert server_version is not None, "serverVersion element not found"

    def test_server_version_value(self):
        """serverVersion should be set to XCEP_SERVER_VERSION."""
        element = RequestFilter.create()

        server_version = element.find(f"{{{NS_CEP}}}serverVersion")
        assert server_version is not None
        assert server_version.text == str(XCEP_SERVER_VERSION)

    def test_server_version_not_nil(self):
        """serverVersion should NOT have xsi:nil attribute."""
        element = RequestFilter.create()

        server_version = element.find(f"{{{NS_CEP}}}serverVersion")
        assert server_version is not None

        nil_attr = server_version.get(
            "{http://www.w3.org/2001/XMLSchema-instance}nil"
        )
        assert nil_attr is None, "serverVersion should not be nil"


class TestGetPoliciesCreate:
    """Tests for GetPolicies.create() method."""

    def test_creates_get_policies_element(self):
        """create() should return a GetPolicies element."""
        element = GetPolicies.create()

        assert element.tag == f"{{{NS_CEP}}}GetPolicies"

    def test_has_client_element(self):
        """GetPolicies should contain client element."""
        element = GetPolicies.create()

        client = element.find(f"{{{NS_CEP}}}client")
        assert client is not None, "client element not found"

    def test_has_request_filter_element(self):
        """GetPolicies should contain requestFilter element."""
        element = GetPolicies.create()

        request_filter = element.find(f"{{{NS_CEP}}}requestFilter")
        assert request_filter is not None, "requestFilter element not found"

    def test_request_filter_has_version_values(self):
        """requestFilter in GetPolicies should have version values set."""
        element = GetPolicies.create()

        request_filter = element.find(f"{{{NS_CEP}}}requestFilter")
        assert request_filter is not None

        client_version = request_filter.find(f"{{{NS_CEP}}}clientVersion")
        server_version = request_filter.find(f"{{{NS_CEP}}}serverVersion")

        assert client_version is not None
        assert server_version is not None
        assert client_version.text == str(XCEP_CLIENT_VERSION)
        assert server_version.text == str(XCEP_SERVER_VERSION)
