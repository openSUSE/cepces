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

import gc
import re
from collections.abc import Callable, Generator
from contextlib import ExitStack
from typing import Any
from unittest.mock import MagicMock, patch
import pytest
from cepces.krb5 import types as ktypes
from cepces.krb5.core import (
    get_default_keytab_name,
    NAME_EX,
    Principal,
)


class TestPrincipal:
    """Tests for Principal.__str__ and service_type inference."""

    @pytest.fixture
    def make_p(self) -> Generator[Callable[..., Principal], None, None]:
        """Factory that keeps kfuncs patches alive until after the test
        function returns, so Principal.__del__ runs with free_principal
        still mocked and does not call into real C extension code.

        Using plain MagicMock() (no spec) for the context avoids
        _mock_add_spec spec-inspection in __del__, which segfaults in
        Python 3.11 when ctypes objects are involved.
        """
        stack = ExitStack()

        def _factory(
            unparsed_name: str,
            service_type: int | None = None,
        ) -> Principal:
            def mock_unparse(ctx: Any, handle: Any, buf: Any) -> None:
                buf.value = unparsed_name.encode("utf-8")

            ctx = MagicMock()
            stack.enter_context(patch("cepces.krb5.core.kfuncs.parse_name"))
            stack.enter_context(
                patch(
                    "cepces.krb5.core.kfuncs.unparse_name",
                    side_effect=mock_unparse,
                )
            )
            stack.enter_context(
                patch("cepces.krb5.core.kfuncs.free_unparsed_name")
            )
            stack.enter_context(
                patch("cepces.krb5.core.kfuncs.free_principal")
            )
            stack.enter_context(
                patch(
                    "cepces.krb5.core.ktypes.krb5_principal",
                    return_value=MagicMock(),
                )
            )
            return Principal(
                ctx, name=unparsed_name, service_type=service_type
            )

        yield _factory

        gc.collect()  # flush Principal.__del__ while patches still active
        stack.close()

    def test_str_simple_principal(
        self, make_p: Callable[..., Principal]
    ) -> None:
        """__str__ returns primary@realm for user principals."""
        p = make_p("user@EXAMPLE.COM")
        assert str(p) == "user@EXAMPLE.COM"

    def test_str_service_principal(
        self, make_p: Callable[..., Principal]
    ) -> None:
        """__str__ returns primary/instance@realm for service principals."""
        p = make_p("host/node.example.com@EXAMPLE.COM")
        assert str(p) == "host/node.example.com@EXAMPLE.COM"

    def test_type_inferred_enterprise_for_user(
        self, make_p: Callable[..., Principal]
    ) -> None:
        """User principals infer KRB5_NT_ENTERPRISE_PRINCIPAL."""
        p = make_p("user@EXAMPLE.COM")
        assert (
            p.service_type == ktypes.PrincipalType.KRB5_NT_ENTERPRISE_PRINCIPAL
        )

    def test_type_inferred_srv_hst_for_service(
        self, make_p: Callable[..., Principal]
    ) -> None:
        """2-component service principals infer KRB5_NT_SRV_HST."""
        p = make_p("host/node.example.com@EXAMPLE.COM")
        assert p.service_type == ktypes.PrincipalType.KRB5_NT_SRV_HST

    def test_str_domain_based_principal(
        self, make_p: Callable[..., Principal]
    ) -> None:
        """__str__ returns primary/instance/domain@realm for 3-part names."""
        p = make_p("cifs/server.example.com/example.com@EXAMPLE.COM")
        assert str(p) == "cifs/server.example.com/example.com@EXAMPLE.COM"

    def test_type_inferred_srv_hst_domain_for_domain_based(
        self, make_p: Callable[..., Principal]
    ) -> None:
        """Domain-based (3-component) service principals infer
        KRB5_NT_SRV_HST_DOMAIN."""
        p = make_p("cifs/server.example.com/example.com@EXAMPLE.COM")
        assert p.service_type == ktypes.PrincipalType.KRB5_NT_SRV_HST_DOMAIN

    def test_explicit_service_type_overrides_inference(
        self, make_p: Callable[..., Principal]
    ) -> None:
        """Explicitly passed service_type wins over inference."""
        p = make_p(
            "host/node.example.com@EXAMPLE.COM",
            service_type=ktypes.PrincipalType.KRB5_NT_SRV_HST,
        )
        assert p.service_type == ktypes.PrincipalType.KRB5_NT_SRV_HST


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
