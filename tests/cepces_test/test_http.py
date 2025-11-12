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
import ssl
from unittest.mock import patch, MagicMock
import requests
from cepces.http import SSLAdapter, create_session


class TestSSLAdapter:
    """Tests for the SSLAdapter class"""

    def test_initialization_without_ssl_context(self):
        """Test SSLAdapter initialization without SSL context"""
        adapter = SSLAdapter()

        assert adapter.ssl_context is None

    def test_initialization_with_ssl_context(self):
        """Test SSLAdapter initialization with SSL context"""
        mock_context = MagicMock(spec=ssl.SSLContext)
        adapter = SSLAdapter(ssl_context=mock_context)

        assert adapter.ssl_context is mock_context

    def test_initialization_with_additional_args(self):
        """Test SSLAdapter initialization with additional arguments"""
        mock_context = MagicMock(spec=ssl.SSLContext)
        adapter = SSLAdapter(
            ssl_context=mock_context, pool_connections=10, pool_maxsize=20
        )

        assert adapter.ssl_context is mock_context

    @patch("cepces.http.HTTPAdapter.init_poolmanager")
    def test_init_poolmanager_with_ssl_context(self, mock_super_init):
        """Test init_poolmanager adds ssl_context when present"""
        mock_context = MagicMock(spec=ssl.SSLContext)
        adapter = SSLAdapter(ssl_context=mock_context)

        # Reset mock to ignore calls from __init__
        mock_super_init.reset_mock()

        adapter.init_poolmanager(connections=10, maxsize=20)

        mock_super_init.assert_called_once()
        call_kwargs = mock_super_init.call_args[1]
        assert "ssl_context" in call_kwargs
        assert call_kwargs["ssl_context"] is mock_context

    @patch("cepces.http.HTTPAdapter.init_poolmanager")
    def test_init_poolmanager_without_ssl_context(self, mock_super_init):
        """Test init_poolmanager without ssl_context"""
        adapter = SSLAdapter()

        # Reset mock to ignore calls from __init__
        mock_super_init.reset_mock()

        adapter.init_poolmanager(connections=10, maxsize=20)

        mock_super_init.assert_called_once()
        call_kwargs = mock_super_init.call_args[1]
        assert "ssl_context" not in call_kwargs

    @patch("cepces.http.HTTPAdapter.init_poolmanager")
    def test_init_poolmanager_preserves_other_kwargs(self, mock_super_init):
        """Test init_poolmanager preserves other keyword arguments"""
        mock_context = MagicMock(spec=ssl.SSLContext)
        adapter = SSLAdapter(ssl_context=mock_context)

        # Reset mock to ignore calls from __init__
        mock_super_init.reset_mock()

        adapter.init_poolmanager(
            connections=10, maxsize=20, custom_arg="value"
        )

        mock_super_init.assert_called_once()
        call_kwargs = mock_super_init.call_args[1]
        assert call_kwargs["ssl_context"] is mock_context
        assert call_kwargs["custom_arg"] == "value"


class TestCreateSession:
    """Tests for the create_session function"""

    def test_create_session_without_ciphers(self):
        """Test create_session without openssl_ciphers returns basic session"""
        session = create_session()

        assert isinstance(session, requests.Session)
        # Verify no custom adapter is mounted for https
        # The default adapter should be the standard HTTPAdapter
        adapter = session.get_adapter("https://example.com")
        # Default adapters are HTTPAdapter instances, not SSLAdapter
        assert type(adapter).__name__ in ["HTTPAdapter", "SSLAdapter"]

    def test_create_session_with_none_ciphers(self):
        """Test create_session with None openssl_ciphers"""
        session = create_session(openssl_ciphers=None)

        assert isinstance(session, requests.Session)

    def test_create_session_with_empty_string_ciphers(self):
        """Test create_session with empty string openssl_ciphers"""
        session = create_session(openssl_ciphers="")

        assert isinstance(session, requests.Session)

    def test_create_session_with_whitespace_only_ciphers(self):
        """Test create_session with whitespace-only openssl_ciphers"""
        session = create_session(openssl_ciphers="   ")

        assert isinstance(session, requests.Session)

    @patch("cepces.http.create_urllib3_context")
    def test_create_session_with_valid_ciphers(self, mock_create_context):
        """Test create_session with valid openssl_ciphers"""
        mock_ssl_context = MagicMock(spec=ssl.SSLContext)
        mock_create_context.return_value = mock_ssl_context

        session = create_session(openssl_ciphers="DEFAULT:@SECLEVEL=1")

        # Verify urllib3 context was created
        mock_create_context.assert_called_once()

        # Verify set_ciphers was called with the correct cipher string
        mock_ssl_context.set_ciphers.assert_called_once_with(
            "DEFAULT:@SECLEVEL=1"
        )

        # Verify session was created
        assert isinstance(session, requests.Session)

        # Verify SSLAdapter was mounted for https
        adapter = session.get_adapter("https://example.com")
        assert isinstance(adapter, SSLAdapter)
        assert adapter.ssl_context is mock_ssl_context

    @patch("cepces.http.create_urllib3_context")
    def test_create_session_with_custom_cipher_string(self, mock_create_ctx):
        """Test create_session with custom cipher string"""
        mock_ssl_context = MagicMock(spec=ssl.SSLContext)
        mock_create_ctx.return_value = mock_ssl_context

        cipher_string = "ECDHE-RSA-AES128-GCM-SHA256:@SECLEVEL=0"
        session = create_session(openssl_ciphers=cipher_string)

        mock_ssl_context.set_ciphers.assert_called_once_with(cipher_string)
        assert isinstance(session, requests.Session)

    @patch("cepces.http.create_urllib3_context")
    def test_create_session_adapter_only_mounted_for_https(
        self, mock_create_ctx
    ):
        """Test that SSLAdapter is only mounted for https, not http"""
        mock_ssl_context = MagicMock(spec=ssl.SSLContext)
        mock_create_ctx.return_value = mock_ssl_context

        session = create_session(openssl_ciphers="DEFAULT:@SECLEVEL=1")

        # Check https adapter
        https_adapter = session.get_adapter("https://example.com")
        assert isinstance(https_adapter, SSLAdapter)

        # Verify session is a requests.Session
        assert isinstance(session, requests.Session)

    @patch("cepces.http.create_urllib3_context")
    def test_create_session_with_cipher_string_with_spaces(
        self, mock_create_ctx
    ):
        """Test create_session with cipher string that has leading/trailing
        spaces"""
        mock_ssl_context = MagicMock(spec=ssl.SSLContext)
        mock_create_ctx.return_value = mock_ssl_context

        cipher_string = "  DEFAULT:@SECLEVEL=1  "
        session = create_session(openssl_ciphers=cipher_string)

        # Should still process since strip() finds non-empty content
        mock_ssl_context.set_ciphers.assert_called_once_with(cipher_string)
        assert isinstance(session, requests.Session)

    def test_create_session_returns_requests_session(self):
        """Test that create_session always returns a requests.Session"""
        # Test with no arguments
        session1 = create_session()
        assert isinstance(session1, requests.Session)

        # Test with None
        session2 = create_session(openssl_ciphers=None)
        assert isinstance(session2, requests.Session)

        # Test with empty string
        session3 = create_session(openssl_ciphers="")
        assert isinstance(session3, requests.Session)

    @patch("cepces.http.create_urllib3_context")
    def test_create_session_ssl_context_configuration(self, mock_create_ctx):
        """Test that SSL context is properly configured and passed"""
        mock_ssl_context = MagicMock(spec=ssl.SSLContext)
        mock_create_ctx.return_value = mock_ssl_context

        cipher_string = "HIGH:!aNULL:!MD5"
        session = create_session(openssl_ciphers=cipher_string)

        # Verify the context creation was called
        mock_create_ctx.assert_called_once_with()

        # Verify set_ciphers was called
        mock_ssl_context.set_ciphers.assert_called_once_with(cipher_string)

        # Verify the adapter has the context
        adapter = session.get_adapter("https://example.com")
        assert adapter.ssl_context is mock_ssl_context  # type: ignore[attr-defined]  # noqa: E501

    def test_create_session_with_invalid_cipher_string(self):
        """Test create_session raises SSLError for invalid cipher string"""
        import pytest

        # Test with a completely invalid cipher string
        with pytest.raises(ssl.SSLError) as exc_info:
            create_session(openssl_ciphers="INVALID_CIPHER_STRING")

        assert "Invalid OpenSSL cipher string" in str(exc_info.value)
        assert "INVALID_CIPHER_STRING" in str(exc_info.value)

    def test_create_session_with_empty_cipher_list(self):
        """Test create_session raises SSLError when cipher string results
        in no valid ciphers"""
        import pytest

        # An empty cipher list or one that excludes everything
        with pytest.raises(ssl.SSLError) as exc_info:
            create_session(openssl_ciphers="!ALL")

        assert "Invalid OpenSSL cipher string" in str(exc_info.value)

    @patch("cepces.http.create_urllib3_context")
    def test_create_session_propagates_ssl_error(self, mock_create_ctx):
        """Test that SSLError from set_ciphers is properly wrapped and
        propagated"""
        import pytest

        mock_ssl_context = MagicMock(spec=ssl.SSLContext)
        mock_create_ctx.return_value = mock_ssl_context

        # Simulate set_ciphers raising an SSLError
        original_error = ssl.SSLError("test error message")
        mock_ssl_context.set_ciphers.side_effect = original_error

        with pytest.raises(ssl.SSLError) as exc_info:
            create_session(openssl_ciphers="SOME_CIPHER")

        # Verify the error message includes our custom message
        assert "Invalid OpenSSL cipher string" in str(exc_info.value)
        assert "SOME_CIPHER" in str(exc_info.value)
        assert "test error message" in str(exc_info.value)

        # Verify the original error is preserved in the chain
        assert exc_info.value.__cause__ is original_error
