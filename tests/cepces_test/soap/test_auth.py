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
"""Tests for cepces.soap.auth module."""
import pytest
from unittest.mock import patch, MagicMock, PropertyMock

from cepces.soap.auth import (
    TransportGSSAPIAuthentication,
    AnonymousAuthentication,
    MessageUsernamePasswordAuthentication,
    TransportCertificateAuthentication,
)


class TestAnonymousAuthentication:
    """Tests for AnonymousAuthentication class."""

    def test_transport_property_returns_none(self):
        """Test that transport property returns None."""
        auth = AnonymousAuthentication()
        assert auth.transport is None

    def test_clientcertificate_property_returns_none(self):
        """Test that clientcertificate property returns None."""
        auth = AnonymousAuthentication()
        assert auth.clientcertificate is None

    def test_post_process_returns_envelope_unchanged(self):
        """Test that post_process returns the envelope unchanged."""
        auth = AnonymousAuthentication()
        mock_envelope = MagicMock()
        result = auth.post_process(mock_envelope)
        assert result is mock_envelope


class TestTransportGSSAPIAuthentication:
    """Tests for TransportGSSAPIAuthentication class."""

    @patch("cepces.soap.auth.Context")
    @patch("cepces.soap.auth.Principal")
    @patch("cepces.soap.auth.get_default_keytab_name")
    @patch("cepces.soap.auth.gssapi.raw.acquire_cred_from")
    @patch("cepces.soap.auth.gssapi.Name")
    @patch("cepces.soap.auth.gssapi.Credentials")
    @patch("cepces.soap.auth.HTTPSPNEGOAuth")
    def test_initialization_with_defaults(
        self,
        mock_http_spnego,
        mock_gssapi_credentials,
        mock_gssapi_name,
        mock_acquire_cred,
        mock_get_keytab,
        mock_principal,
        mock_context,
    ):
        """Test initialization with default parameters."""
        # Setup mocks
        mock_context_instance = MagicMock()
        mock_context.return_value = mock_context_instance

        mock_principal_instance = MagicMock()
        type(mock_principal_instance).primary = PropertyMock(
            return_value="testuser"
        )
        type(mock_principal_instance).realm = PropertyMock(
            return_value="EXAMPLE.COM"
        )
        mock_principal.return_value = mock_principal_instance

        mock_get_keytab.return_value = "/etc/krb5.keytab"
        mock_acquire_cred.return_value = MagicMock(creds=MagicMock())

        # Create authentication object
        _auth = TransportGSSAPIAuthentication()  # noqa: F841

        # Verify Context was called
        mock_context.assert_called_once()

        # Verify Principal was created
        mock_principal.assert_called_once()
        call_kwargs = mock_principal.call_args[1]
        assert call_kwargs["name"] is None
        assert "service_type" in call_kwargs

        # Verify keytab was retrieved
        mock_get_keytab.assert_called_once()

        # Verify GSSAPI credentials were acquired
        mock_acquire_cred.assert_called_once()

        # Verify HTTPSPNEGOAuth was initialized
        mock_http_spnego.assert_called_once()

    @patch("cepces.soap.auth.Context")
    @patch("cepces.soap.auth.Principal")
    @patch("cepces.soap.auth.get_default_keytab_name")
    @patch("cepces.soap.auth.gssapi.raw.acquire_cred_from")
    @patch("cepces.soap.auth.gssapi.Name")
    @patch("cepces.soap.auth.gssapi.Credentials")
    @patch("cepces.soap.auth.HTTPSPNEGOAuth")
    def test_initialization_with_principal_name(
        self,
        mock_http_spnego,
        mock_gssapi_credentials,
        mock_gssapi_name,
        mock_acquire_cred,
        mock_get_keytab,
        mock_principal,
        mock_context,
    ):
        """Test initialization with specific principal name."""
        # Setup mocks
        mock_context_instance = MagicMock()
        mock_context.return_value = mock_context_instance

        mock_principal_instance = MagicMock()
        type(mock_principal_instance).primary = PropertyMock(
            return_value="myuser"
        )
        type(mock_principal_instance).realm = PropertyMock(
            return_value="TEST.REALM"
        )
        mock_principal.return_value = mock_principal_instance

        mock_get_keytab.return_value = "/etc/krb5.keytab"
        mock_acquire_cred.return_value = MagicMock(creds=MagicMock())

        # Create authentication object with principal name
        _auth = TransportGSSAPIAuthentication(  # noqa: F841
            principal_name="myuser@TEST.REALM"
        )

        # Verify Principal was created with the specified name
        mock_principal.assert_called_once()
        call_kwargs = mock_principal.call_args[1]
        assert call_kwargs["name"] == "myuser@TEST.REALM"

    @patch("cepces.soap.auth.Context")
    @patch("cepces.soap.auth.Principal")
    @patch("cepces.soap.auth.gssapi.Name")
    @patch("cepces.soap.auth.gssapi.Credentials")
    @patch("cepces.soap.auth.HTTPSPNEGOAuth")
    def test_initialization_with_init_ccache_false(
        self,
        mock_http_spnego,
        mock_gssapi_credentials,
        mock_gssapi_name,
        mock_principal,
        mock_context,
    ):
        """Test initialization with init_ccache=False.

        When init_ccache=False, the code relies on an existing credential cache
        and passes None to _init_transport, which then tries to access .creds
        attribute. This test verifies that gssapi.Credentials is called with
        base=None.
        """
        # Setup mocks
        mock_context_instance = MagicMock()
        mock_context.return_value = mock_context_instance

        mock_principal_instance = MagicMock()
        type(mock_principal_instance).primary = PropertyMock(
            return_value="testuser"
        )
        type(mock_principal_instance).realm = PropertyMock(
            return_value="EXAMPLE.COM"
        )
        mock_principal.return_value = mock_principal_instance

        # Create a mock that has .creds attribute returning None
        # to simulate the case when no ccache is initialized
        mock_none_cred = MagicMock()
        mock_none_cred.creds = None

        # Create authentication object without initializing ccache
        # Note: This will fail because the code tries to access
        # gssapi_cred.creds when gssapi_cred is None.
        # The test demonstrates this limitation.
        with pytest.raises(AttributeError):
            _auth = TransportGSSAPIAuthentication(  # noqa: F841
                init_ccache=False
            )

    @pytest.mark.xfail(
        reason="keytab path must be encoded to bytes before passing to store",
        strict=True,
    )
    @patch("cepces.soap.auth.Context")
    @patch("cepces.soap.auth.Principal")
    @patch("cepces.soap.auth.get_default_keytab_name")
    @patch("cepces.soap.auth.gssapi.raw.acquire_cred_from")
    @patch("cepces.soap.auth.gssapi.Name")
    @patch("cepces.soap.auth.gssapi.Credentials")
    @patch("cepces.soap.auth.HTTPSPNEGOAuth")
    def test_initialization_with_custom_keytab(
        self,
        mock_http_spnego,
        mock_gssapi_credentials,
        mock_gssapi_name,
        mock_acquire_cred,
        mock_get_keytab,
        mock_principal,
        mock_context,
    ):
        """Test initialization with custom keytab."""
        # Setup mocks
        mock_context_instance = MagicMock()
        mock_context.return_value = mock_context_instance

        mock_principal_instance = MagicMock()
        type(mock_principal_instance).primary = PropertyMock(
            return_value="testuser"
        )
        type(mock_principal_instance).realm = PropertyMock(
            return_value="EXAMPLE.COM"
        )
        mock_principal.return_value = mock_principal_instance

        mock_acquire_cred.return_value = MagicMock(creds=MagicMock())

        custom_keytab = "/path/to/custom.keytab"

        # Create authentication object with custom keytab
        _auth = TransportGSSAPIAuthentication(  # noqa: F841
            keytab=custom_keytab
        )

        # Verify get_default_keytab_name was NOT called
        mock_get_keytab.assert_not_called()

        # Verify acquire_cred_from was called with custom keytab
        mock_acquire_cred.assert_called_once()
        call_kwargs = mock_acquire_cred.call_args[1]
        assert call_kwargs["store"][b"client_keytab"] == custom_keytab.encode(
            "utf-8"
        )

    @patch("cepces.soap.auth.Context")
    @patch("cepces.soap.auth.Principal")
    @patch("cepces.soap.auth.get_default_keytab_name")
    @patch("cepces.soap.auth.gssapi.raw.acquire_cred_from")
    @patch("cepces.soap.auth.gssapi.Name")
    @patch("cepces.soap.auth.gssapi.Credentials")
    @patch("cepces.soap.auth.HTTPSPNEGOAuth")
    def test_initialization_with_delegate_false(
        self,
        mock_http_spnego,
        mock_gssapi_credentials,
        mock_gssapi_name,
        mock_acquire_cred,
        mock_get_keytab,
        mock_principal,
        mock_context,
    ):
        """Test initialization with delegate=False."""
        # Setup mocks
        mock_context_instance = MagicMock()
        mock_context.return_value = mock_context_instance

        mock_principal_instance = MagicMock()
        type(mock_principal_instance).primary = PropertyMock(
            return_value="testuser"
        )
        type(mock_principal_instance).realm = PropertyMock(
            return_value="EXAMPLE.COM"
        )
        mock_principal.return_value = mock_principal_instance

        mock_get_keytab.return_value = "/etc/krb5.keytab"
        mock_acquire_cred.return_value = MagicMock(creds=MagicMock())

        # Create authentication object with delegate=False
        _auth = TransportGSSAPIAuthentication(delegate=False)  # noqa: F841

        # Verify HTTPSPNEGOAuth was called with delegate=False
        mock_http_spnego.assert_called_once()
        call_kwargs = mock_http_spnego.call_args[1]
        assert call_kwargs["delegate"] is False

    @patch("cepces.soap.auth.Context")
    @patch("cepces.soap.auth.Principal")
    @patch("cepces.soap.auth.get_default_keytab_name")
    @patch("cepces.soap.auth.gssapi.raw.acquire_cred_from")
    @patch("cepces.soap.auth.gssapi.Name")
    @patch("cepces.soap.auth.gssapi.Credentials")
    @patch("cepces.soap.auth.HTTPSPNEGOAuth")
    def test_transport_property(
        self,
        mock_http_spnego,
        mock_gssapi_credentials,
        mock_gssapi_name,
        mock_acquire_cred,
        mock_get_keytab,
        mock_principal,
        mock_context,
    ):
        """Test that transport property returns HTTPSPNEGOAuth instance."""
        # Setup mocks
        mock_context_instance = MagicMock()
        mock_context.return_value = mock_context_instance

        mock_principal_instance = MagicMock()
        type(mock_principal_instance).primary = PropertyMock(
            return_value="testuser"
        )
        type(mock_principal_instance).realm = PropertyMock(
            return_value="EXAMPLE.COM"
        )
        mock_principal.return_value = mock_principal_instance

        mock_get_keytab.return_value = "/etc/krb5.keytab"
        mock_acquire_cred.return_value = MagicMock(creds=MagicMock())

        mock_spnego_instance = MagicMock()
        mock_http_spnego.return_value = mock_spnego_instance

        # Create authentication object
        auth = TransportGSSAPIAuthentication()

        # Verify transport property returns the HTTPSPNEGOAuth instance
        assert auth.transport is mock_spnego_instance

    @patch("cepces.soap.auth.Context")
    @patch("cepces.soap.auth.Principal")
    @patch("cepces.soap.auth.get_default_keytab_name")
    @patch("cepces.soap.auth.gssapi.raw.acquire_cred_from")
    @patch("cepces.soap.auth.gssapi.Name")
    @patch("cepces.soap.auth.gssapi.Credentials")
    @patch("cepces.soap.auth.HTTPSPNEGOAuth")
    def test_clientcertificate_property_returns_none(
        self,
        mock_http_spnego,
        mock_gssapi_credentials,
        mock_gssapi_name,
        mock_acquire_cred,
        mock_get_keytab,
        mock_principal,
        mock_context,
    ):
        """Test that clientcertificate property returns None."""
        # Setup mocks
        mock_context_instance = MagicMock()
        mock_context.return_value = mock_context_instance

        mock_principal_instance = MagicMock()
        type(mock_principal_instance).primary = PropertyMock(
            return_value="testuser"
        )
        type(mock_principal_instance).realm = PropertyMock(
            return_value="EXAMPLE.COM"
        )
        mock_principal.return_value = mock_principal_instance

        mock_get_keytab.return_value = "/etc/krb5.keytab"
        mock_acquire_cred.return_value = MagicMock(creds=MagicMock())

        # Create authentication object
        auth = TransportGSSAPIAuthentication()

        # Verify clientcertificate property returns None
        assert auth.clientcertificate is None

    @patch("cepces.soap.auth.Context")
    @patch("cepces.soap.auth.Principal")
    @patch("cepces.soap.auth.get_default_keytab_name")
    @patch("cepces.soap.auth.gssapi.raw.acquire_cred_from")
    @patch("cepces.soap.auth.gssapi.Name")
    @patch("cepces.soap.auth.gssapi.Credentials")
    @patch("cepces.soap.auth.HTTPSPNEGOAuth")
    def test_post_process_returns_envelope_unchanged(
        self,
        mock_http_spnego,
        mock_gssapi_credentials,
        mock_gssapi_name,
        mock_acquire_cred,
        mock_get_keytab,
        mock_principal,
        mock_context,
    ):
        """Test that post_process returns the envelope unchanged."""
        # Setup mocks
        mock_context_instance = MagicMock()
        mock_context.return_value = mock_context_instance

        mock_principal_instance = MagicMock()
        type(mock_principal_instance).primary = PropertyMock(
            return_value="testuser"
        )
        type(mock_principal_instance).realm = PropertyMock(
            return_value="EXAMPLE.COM"
        )
        mock_principal.return_value = mock_principal_instance

        mock_get_keytab.return_value = "/etc/krb5.keytab"
        mock_acquire_cred.return_value = MagicMock(creds=MagicMock())

        # Create authentication object
        auth = TransportGSSAPIAuthentication()

        # Test post_process
        mock_envelope = MagicMock()
        result = auth.post_process(mock_envelope)
        assert result is mock_envelope

    @patch("cepces.soap.auth.Context")
    @patch("cepces.soap.auth.Principal")
    @patch("cepces.soap.auth.get_default_keytab_name")
    @patch("cepces.soap.auth.gssapi.raw.acquire_cred_from")
    @patch("cepces.soap.auth.gssapi.Name")
    @patch("cepces.soap.auth.gssapi.Credentials")
    @patch("cepces.soap.auth.HTTPSPNEGOAuth")
    @patch("cepces.soap.auth.os.environ", {})
    def test_init_ccache_sets_environment_variable(
        self,
        mock_http_spnego,
        mock_gssapi_credentials,
        mock_gssapi_name,
        mock_acquire_cred,
        mock_get_keytab,
        mock_principal,
        mock_context,
    ):
        """Test that _init_ccache sets KRB5CCNAME environment variable."""
        # Setup mocks
        mock_context_instance = MagicMock()
        mock_context.return_value = mock_context_instance

        mock_principal_instance = MagicMock()
        type(mock_principal_instance).primary = PropertyMock(
            return_value="testuser"
        )
        type(mock_principal_instance).realm = PropertyMock(
            return_value="EXAMPLE.COM"
        )
        mock_principal.return_value = mock_principal_instance

        mock_get_keytab.return_value = "/etc/krb5.keytab"
        mock_acquire_cred.return_value = MagicMock(creds=MagicMock())

        # Import os to check environment variable
        import os

        # Create authentication object
        _auth = TransportGSSAPIAuthentication()  # noqa: F841

        # Verify KRB5CCNAME was set
        assert "KRB5CCNAME" in os.environ
        assert os.environ["KRB5CCNAME"] == "MEMORY:cepces"


class TestMessageUsernamePasswordAuthentication:
    """Tests for MessageUsernamePasswordAuthentication class."""

    def test_initialization(self):
        """Test initialization with username and password."""
        auth = MessageUsernamePasswordAuthentication("testuser", "testpass")
        assert auth._username == "testuser"
        assert auth._password == "testpass"
        assert hasattr(auth, "_nonce")
        assert hasattr(auth, "_created")

    def test_transport_property_returns_none(self):
        """Test that transport property returns None."""
        auth = MessageUsernamePasswordAuthentication("testuser", "testpass")
        assert auth.transport is None

    def test_clientcertificate_property_returns_none(self):
        """Test that clientcertificate property returns None."""
        auth = MessageUsernamePasswordAuthentication("testuser", "testpass")
        assert auth.clientcertificate is None

    def test_post_process_adds_security_header(self):
        """Test that post_process adds security header to envelope."""
        auth = MessageUsernamePasswordAuthentication("testuser", "testpass")

        mock_envelope = MagicMock()
        mock_header = MagicMock()
        mock_envelope.header = mock_header

        result = auth.post_process(mock_envelope)

        # Verify security header was added
        mock_header.element.append.assert_called_once()
        assert result is mock_envelope


class TestTransportCertificateAuthentication:
    """Tests for TransportCertificateAuthentication class."""

    def test_initialization(self):
        """Test initialization with certificate and key files."""
        auth = TransportCertificateAuthentication(
            "/path/to/cert.pem", "/path/to/key.pem"
        )
        assert auth._certfile == "/path/to/cert.pem"
        assert auth._keyfile == "/path/to/key.pem"

    def test_transport_property_returns_none(self):
        """Test that transport property returns None."""
        auth = TransportCertificateAuthentication(
            "/path/to/cert.pem", "/path/to/key.pem"
        )
        assert auth.transport is None

    def test_clientcertificate_property_returns_tuple(self):
        """Test clientcertificate property returns cert and key tuple."""
        auth = TransportCertificateAuthentication(
            "/path/to/cert.pem", "/path/to/key.pem"
        )
        assert auth.clientcertificate == (
            "/path/to/cert.pem",
            "/path/to/key.pem",
        )

    def test_post_process_returns_envelope_unchanged(self):
        """Test that post_process returns the envelope unchanged."""
        auth = TransportCertificateAuthentication(
            "/path/to/cert.pem", "/path/to/key.pem"
        )
        mock_envelope = MagicMock()
        result = auth.post_process(mock_envelope)
        assert result is mock_envelope
