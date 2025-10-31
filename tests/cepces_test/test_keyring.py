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
import pytest
from unittest.mock import patch, MagicMock
import subprocess
from cepces.keyring import (
    KeyringHandler,
    KeyringError,
    KeyringNotFoundError,
    KeyringOperationError,
)


@patch("cepces.keyring.shutil.which")
def test_keyctl_handler_initialization_with_keyctl_available(mock_which):
    """Test initialization when keyctl is available"""
    mock_which.return_value = "/usr/bin/keyctl"

    handler = KeyringHandler("test-service")

    assert handler.service_name == "test-service"
    assert handler._keyctl_available is True
    mock_which.assert_called_once_with("keyctl")


@patch("cepces.keyring.shutil.which")
def test_keyctl_handler_initialization_with_keyctl_unavailable(mock_which):
    """Test initialization when keyctl is not available"""
    mock_which.return_value = None

    handler = KeyringHandler("test-service")

    assert handler.service_name == "test-service"
    assert handler._keyctl_available is False
    mock_which.assert_called_once_with("keyctl")


@patch("cepces.keyring.shutil.which")
def test_keyctl_handler_initialization_with_default_service_name(mock_which):
    """Test initialization with default service name"""
    mock_which.return_value = "/usr/bin/keyctl"

    handler = KeyringHandler()

    assert handler.service_name == "cepces"
    assert handler._keyctl_available is True


def test_keyctl_handler_get_key_description():
    """Test key description generation"""
    with patch("cepces.keyring.shutil.which", return_value="/usr/bin/keyctl"):
        handler = KeyringHandler("test-service")

    key_desc = handler._get_key_description("testuser")
    assert key_desc == "test-service:testuser"


@patch("cepces.keyring.shutil.which")
@patch("cepces.keyring.subprocess.run")
def test_keyctl_handler_get_password_success(mock_run, mock_which):
    """Test successful password retrieval"""
    mock_which.return_value = "/usr/bin/keyctl"

    # Mock the two subprocess calls
    mock_run.side_effect = [
        MagicMock(stdout="12345\n", returncode=0),  # keyctl request
        MagicMock(stdout="test_password", returncode=0),  # keyctl pipe
    ]

    handler = KeyringHandler("test-service")
    password = handler.get_password("testuser")

    assert password == "test_password"
    assert mock_run.call_count == 2

    # Verify first call (keyctl request)
    first_call = mock_run.call_args_list[0]
    assert first_call[0][0] == [
        "/usr/bin/keyctl",
        "request",
        "user",
        "test-service:testuser",
    ]

    # Verify second call (keyctl pipe)
    second_call = mock_run.call_args_list[1]
    assert second_call[0][0] == ["/usr/bin/keyctl", "pipe", "12345"]


@patch("cepces.keyring.shutil.which")
def test_keyctl_handler_get_password_with_no_username(mock_which):
    """Test password retrieval with no username"""
    mock_which.return_value = "/usr/bin/keyctl"

    handler = KeyringHandler("test-service")
    password = handler.get_password("")

    assert password is None


@patch("cepces.keyring.shutil.which")
def test_keyctl_handler_get_password_when_keyctl_unavailable(mock_which):
    """Test password retrieval when keyctl is unavailable"""
    mock_which.return_value = None

    handler = KeyringHandler("test-service")
    password = handler.get_password("testuser")

    assert password is None


@patch("cepces.keyring.shutil.which")
@patch("cepces.keyring.subprocess.run")
def test_keyctl_handler_get_password_not_found(mock_run, mock_which):
    """Test password retrieval when key not found"""
    mock_which.return_value = "/usr/bin/keyctl"
    mock_run.side_effect = subprocess.CalledProcessError(
        1, "keyctl", stderr="Key not found"
    )

    handler = KeyringHandler("test-service")
    password = handler.get_password("testuser")

    assert password is None


@patch("cepces.keyring.shutil.which")
@patch("cepces.keyring.subprocess.run")
def test_keyctl_handler_set_password_success(mock_run, mock_which):
    """Test successful password storage"""
    mock_which.return_value = "/usr/bin/keyctl"
    mock_run.return_value = MagicMock(returncode=0)

    handler = KeyringHandler("test-service")
    handler.set_password("testuser", "test_password")

    mock_run.assert_called_once()
    call_args = mock_run.call_args
    assert call_args[0][0] == [
        "/usr/bin/keyctl",
        "padd",
        "user",
        "test-service:testuser",
        "@u",
    ]
    assert call_args[1]["input"] == "test_password"
    assert call_args[1]["check"] is True


@patch("cepces.keyring.shutil.which")
def test_keyctl_handler_set_password_when_keyctl_unavailable(mock_which):
    """Test password storage when keyctl is unavailable"""
    mock_which.return_value = None

    handler = KeyringHandler("test-service")

    with pytest.raises(KeyringNotFoundError) as exc_info:
        handler.set_password("testuser", "test_password")

    assert "keyctl utility not found" in str(exc_info.value)


@patch("cepces.keyring.shutil.which")
def test_keyctl_handler_set_password_with_empty_username(mock_which):
    """Test password storage with empty username"""
    mock_which.return_value = "/usr/bin/keyctl"

    handler = KeyringHandler("test-service")

    with pytest.raises(KeyringOperationError) as exc_info:
        handler.set_password("", "test_password")

    assert "Username and password are required" in str(exc_info.value)


@patch("cepces.keyring.shutil.which")
def test_keyctl_handler_set_password_with_empty_password(mock_which):
    """Test password storage with empty password"""
    mock_which.return_value = "/usr/bin/keyctl"

    handler = KeyringHandler("test-service")

    with pytest.raises(KeyringOperationError) as exc_info:
        handler.set_password("testuser", "")

    assert "Username and password are required" in str(exc_info.value)


@patch("cepces.keyring.shutil.which")
@patch("cepces.keyring.subprocess.run")
def test_keyctl_handler_set_password_subprocess_error(mock_run, mock_which):
    """Test password storage when subprocess fails"""
    mock_which.return_value = "/usr/bin/keyctl"
    mock_run.side_effect = subprocess.CalledProcessError(
        1, "keyctl", stderr="Permission denied"
    )

    handler = KeyringHandler("test-service")

    with pytest.raises(KeyringOperationError) as exc_info:
        handler.set_password("testuser", "test_password")

    assert "Failed to store password" in str(exc_info.value)


@patch("cepces.keyring.shutil.which")
@patch("cepces.keyring.subprocess.run")
def test_keyctl_handler_delete_password_success(mock_run, mock_which):
    """Test successful password deletion"""
    mock_which.return_value = "/usr/bin/keyctl"

    # Mock the two subprocess calls
    mock_run.side_effect = [
        MagicMock(stdout="12345\n", returncode=0),  # keyctl request
        MagicMock(returncode=0),  # keyctl unlink
    ]

    handler = KeyringHandler("test-service")
    result = handler.delete_password("testuser")

    assert result is True
    assert mock_run.call_count == 2

    # Verify first call (keyctl request)
    first_call = mock_run.call_args_list[0]
    assert first_call[0][0] == [
        "/usr/bin/keyctl",
        "request",
        "user",
        "test-service:testuser",
    ]

    # Verify second call (keyctl unlink)
    second_call = mock_run.call_args_list[1]
    assert second_call[0][0] == ["/usr/bin/keyctl", "unlink", "12345", "@u"]


@patch("cepces.keyring.shutil.which")
def test_keyctl_handler_delete_password_with_no_username(mock_which):
    """Test password deletion with no username"""
    mock_which.return_value = "/usr/bin/keyctl"

    handler = KeyringHandler("test-service")
    result = handler.delete_password("")

    assert result is False


@patch("cepces.keyring.shutil.which")
def test_keyctl_handler_delete_password_when_keyctl_unavailable(mock_which):
    """Test password deletion when keyctl is unavailable"""
    mock_which.return_value = None

    handler = KeyringHandler("test-service")
    result = handler.delete_password("testuser")

    assert result is False


@patch("cepces.keyring.shutil.which")
@patch("cepces.keyring.subprocess.run")
def test_keyctl_handler_delete_password_not_found(mock_run, mock_which):
    """Test password deletion when key not found"""
    mock_which.return_value = "/usr/bin/keyctl"
    mock_run.side_effect = subprocess.CalledProcessError(
        1, "keyctl", stderr="Key not found"
    )

    handler = KeyringHandler("test-service")
    result = handler.delete_password("testuser")

    assert result is False


def test_keyctl_error_hierarchy():
    """Test exception hierarchy"""
    assert issubclass(KeyringNotFoundError, KeyringError)
    assert issubclass(KeyringOperationError, KeyringError)
    assert issubclass(KeyringError, Exception)
