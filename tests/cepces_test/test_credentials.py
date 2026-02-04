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
from cepces.credentials import (
    CredentialsHandler,
    CredentialsError,
    CredentialsNotFoundError,
    CredentialsOperationError,
)


@patch("cepces.credentials.shutil.which")
def test_credentials_handler_initialization_with_pinentry_available(
    mock_which: MagicMock,
) -> None:
    """Test initialization when pinentry is available"""
    mock_which.return_value = "/usr/bin/pinentry"

    handler = CredentialsHandler("Test Title")

    assert handler.title == "Test Title"
    assert handler._pinentry_available is True
    # Now checks all three handlers (pinentry, kdialog, zenity)
    assert mock_which.call_count == 3
    mock_which.assert_any_call("pinentry")


@patch("cepces.credentials.shutil.which")
def test_credentials_handler_initialization_with_pinentry_unavailable(
    mock_which: MagicMock,
) -> None:
    """Test initialization when pinentry is not available"""
    mock_which.return_value = None

    handler = CredentialsHandler("Test Title")

    assert handler.title == "Test Title"
    assert handler._pinentry_available is False
    # Now checks all three handlers (pinentry, kdialog, zenity)
    assert mock_which.call_count == 3
    mock_which.assert_any_call("pinentry")


@patch("cepces.credentials.shutil.which")
def test_credentials_handler_initialization_with_default_title(
    mock_which: MagicMock,
) -> None:
    """Test initialization with default title"""
    mock_which.return_value = "/usr/bin/pinentry"

    handler = CredentialsHandler()

    assert handler.title == "Authentication Required"
    assert handler._pinentry_available is True


@patch("cepces.credentials.shutil.which")
def test_credentials_handler_is_supported_available(
    mock_which: MagicMock,
) -> None:
    """Test is_supported when pinentry is available"""
    mock_which.return_value = "/usr/bin/pinentry"

    handler = CredentialsHandler()
    result = handler.is_supported()

    assert result is True


@patch("cepces.credentials.shutil.which")
def test_credentials_handler_is_supported_unavailable(
    mock_which: MagicMock,
) -> None:
    """Test is_supported when pinentry is not available"""
    mock_which.return_value = None

    handler = CredentialsHandler()
    result = handler.is_supported()

    assert result is False


@patch("cepces.credentials.shutil.which")
@patch("cepces.credentials.subprocess.run")
def test_credentials_handler_run_pinentry_success(
    mock_run: MagicMock, mock_which: MagicMock
) -> None:
    """Test successful pinentry execution"""
    mock_which.return_value = "/usr/bin/pinentry"
    mock_run.return_value = MagicMock(
        stdout="OK\nD test_data\nOK\n", returncode=0
    )

    handler = CredentialsHandler()
    responses = handler.run_pinentry(["GETPIN"])

    assert responses["data"] == "test_data"
    assert responses["ok"] is True
    mock_run.assert_called_once()
    call_args = mock_run.call_args
    assert call_args[0][0] == ["/usr/bin/pinentry"]
    assert "GETPIN\nBYE\n" in call_args[1]["input"]


@patch("cepces.credentials.shutil.which")
def test_credentials_handler_run_pinentry_when_unavailable(
    mock_which: MagicMock,
) -> None:
    """Test run_pinentry when pinentry is unavailable"""
    mock_which.return_value = None

    handler = CredentialsHandler()

    with pytest.raises(CredentialsNotFoundError) as exc_info:
        handler.run_pinentry(["GETPIN"])

    assert "pinentry utility not found" in str(exc_info.value)


@patch("cepces.credentials.shutil.which")
@patch("cepces.credentials.subprocess.run")
def test_credentials_handler_run_pinentry_error_response(
    mock_run: MagicMock, mock_which: MagicMock
) -> None:
    """Test pinentry execution with error response"""
    mock_which.return_value = "/usr/bin/pinentry"
    mock_run.return_value = MagicMock(
        stdout="ERR 83886179 Operation cancelled\n", returncode=0
    )

    handler = CredentialsHandler()
    responses = handler.run_pinentry(["GETPIN"])

    assert "error" in responses
    error = responses["error"]
    assert isinstance(error, str)  # "error" key always contains str
    assert "Operation cancelled" in error


@patch("cepces.credentials.shutil.which")
@patch("cepces.credentials.subprocess.run")
def test_credentials_handler_prompt_password_success(
    mock_run: MagicMock, mock_which: MagicMock
) -> None:
    """Test successful password prompt"""
    mock_which.return_value = "/usr/bin/pinentry"
    mock_run.return_value = MagicMock(
        stdout="OK\nD secret_password\nOK\n", returncode=0
    )

    handler = CredentialsHandler("Login")
    password = handler.prompt_password(
        description="Enter password", prompt="Password:"
    )

    assert password == "secret_password"
    mock_run.assert_called_once()
    call_args = mock_run.call_args
    input_data = call_args[1]["input"]
    assert "SETTITLE Login" in input_data
    assert "SETDESC Enter password" in input_data
    assert "SETPROMPT Password:" in input_data
    assert "GETPIN" in input_data


@patch("cepces.credentials.shutil.which")
@patch("cepces.credentials.subprocess.run")
def test_credentials_handler_prompt_password_cancelled(
    mock_run: MagicMock, mock_which: MagicMock
) -> None:
    """Test password prompt when user cancels"""
    mock_which.return_value = "/usr/bin/pinentry"
    mock_run.return_value = MagicMock(
        stdout="ERR 83886179 Operation cancelled\n", returncode=0
    )

    handler = CredentialsHandler()
    password = handler.prompt_password()

    assert password is None


@patch("cepces.credentials.shutil.which")
def test_credentials_handler_prompt_password_when_unavailable(
    mock_which: MagicMock,
) -> None:
    """Test password prompt when pinentry is unavailable"""
    mock_which.return_value = None

    handler = CredentialsHandler()
    password = handler.prompt_password()

    assert password is None


@patch("cepces.credentials.shutil.which")
@patch("cepces.credentials.subprocess.run")
def test_credentials_handler_prompt_password_no_data(
    mock_run: MagicMock, mock_which: MagicMock
) -> None:
    """Test password prompt with no data returned"""
    mock_which.return_value = "/usr/bin/pinentry"
    mock_run.return_value = MagicMock(stdout="OK\n", returncode=0)

    handler = CredentialsHandler()
    password = handler.prompt_password()

    assert password is None


@patch("cepces.credentials.shutil.which")
@patch("cepces.credentials.subprocess.run")
def test_credentials_handler_prompt_credentials_success(
    mock_run: MagicMock, mock_which: MagicMock
) -> None:
    """Test successful credentials prompt"""
    mock_which.return_value = "/usr/bin/pinentry"

    # Mock two calls: one for username, one for password
    mock_run.side_effect = [
        MagicMock(stdout="OK\nD testuser\nOK\n", returncode=0),  # username
        MagicMock(stdout="OK\nD testpass\nOK\n", returncode=0),  # password
    ]

    handler = CredentialsHandler("Login")
    username, password = handler.prompt_credentials(
        username_description="Enter username",
        password_description="Enter password",
    )

    assert username == "testuser"
    assert password == "testpass"
    assert mock_run.call_count == 2

    # Verify first call (username)
    first_call = mock_run.call_args_list[0]
    username_input = first_call[1]["input"]
    assert "SETTITLE Login" in username_input
    assert "SETDESC Enter username" in username_input
    assert "SETPROMPT Username:" in username_input

    # Verify second call (password)
    second_call = mock_run.call_args_list[1]
    password_input = second_call[1]["input"]
    assert "SETTITLE Login" in password_input
    assert "SETDESC Enter password" in password_input
    assert "SETPROMPT Password:" in password_input


@patch("cepces.credentials.shutil.which")
@patch("cepces.credentials.subprocess.run")
def test_credentials_handler_prompt_credentials_username_cancelled(
    mock_run: MagicMock, mock_which: MagicMock
) -> None:
    """Test credentials prompt when username is cancelled"""
    mock_which.return_value = "/usr/bin/pinentry"
    mock_run.return_value = MagicMock(
        stdout="ERR 83886179 Operation cancelled\n", returncode=0
    )

    handler = CredentialsHandler()
    username, password = handler.prompt_credentials()

    assert username is None
    assert password is None
    # Should only call once for username, not proceed to password
    assert mock_run.call_count == 1


@patch("cepces.credentials.shutil.which")
@patch("cepces.credentials.subprocess.run")
def test_credentials_handler_prompt_credentials_password_cancelled(
    mock_run: MagicMock, mock_which: MagicMock
) -> None:
    """Test credentials prompt when password is cancelled"""
    mock_which.return_value = "/usr/bin/pinentry"

    # Username succeeds, password cancelled
    mock_run.side_effect = [
        MagicMock(stdout="OK\nD testuser\nOK\n", returncode=0),  # username
        MagicMock(
            stdout="ERR 83886179 Operation cancelled\n", returncode=0
        ),  # password
    ]

    handler = CredentialsHandler()
    username, password = handler.prompt_credentials()

    assert username is None
    assert password is None
    assert mock_run.call_count == 2


@patch("cepces.credentials.shutil.which")
@patch("cepces.credentials.subprocess.run")
def test_credentials_handler_prompt_credentials_no_username_data(
    mock_run: MagicMock, mock_which: MagicMock
) -> None:
    """Test credentials prompt when no username data returned"""
    mock_which.return_value = "/usr/bin/pinentry"
    mock_run.return_value = MagicMock(stdout="OK\n", returncode=0)

    handler = CredentialsHandler()
    username, password = handler.prompt_credentials()

    assert username is None
    assert password is None


@patch("cepces.credentials.shutil.which")
def test_credentials_handler_prompt_credentials_when_unavailable(
    mock_which: MagicMock,
) -> None:
    """Test credentials prompt when pinentry is unavailable"""
    mock_which.return_value = None

    handler = CredentialsHandler()
    username, password = handler.prompt_credentials()

    assert username is None
    assert password is None


@patch("cepces.credentials.shutil.which")
@patch("cepces.credentials.subprocess.run")
def test_credentials_handler_run_pinentry_file_not_found(
    mock_run: MagicMock, mock_which: MagicMock
) -> None:
    """Test run_pinentry when command raises FileNotFoundError"""
    mock_which.return_value = "/usr/bin/pinentry"
    mock_run.side_effect = FileNotFoundError()

    handler = CredentialsHandler()

    with pytest.raises(CredentialsNotFoundError) as exc_info:
        handler.run_pinentry(["GETPIN"])

    assert "pinentry utility not found" in str(exc_info.value)


@patch("cepces.credentials.shutil.which")
@patch("cepces.credentials.subprocess.run")
def test_credentials_handler_prompt_password_with_defaults(
    mock_run: MagicMock, mock_which: MagicMock
) -> None:
    """Test password prompt with default parameters"""
    mock_which.return_value = "/usr/bin/pinentry"
    mock_run.return_value = MagicMock(
        stdout="OK\nD password123\nOK\n", returncode=0
    )

    handler = CredentialsHandler()
    password = handler.prompt_password()

    assert password == "password123"
    call_args = mock_run.call_args
    input_data = call_args[1]["input"]
    assert "SETDESC Enter your password" in input_data
    assert "SETPROMPT Password:" in input_data


def test_credentials_error_hierarchy() -> None:
    """Test exception hierarchy"""
    assert issubclass(CredentialsNotFoundError, CredentialsError)
    assert issubclass(CredentialsOperationError, CredentialsError)
    assert issubclass(CredentialsError, Exception)
