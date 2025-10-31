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
"""Module for handling kernel keyring operations via keyctl utility."""
import shutil
import subprocess
from cepces import Base


# Use the user keyring
KEYRING = "@u"


class KeyringError(Exception):
    """Base exception for keyctl operations."""


class KeyringNotFoundError(KeyringError):
    """Exception raised when keyctl utility is not found."""


class KeyringOperationError(KeyringError):
    """Exception raised when keyctl operation fails."""


class KeyringHandler(Base):
    """Handler for kernel keyring operations using keyctl utility."""

    def __init__(self, service_name: str = "cepces"):
        """Initialize the KeyringHandler.

        Args:
            service_name: The service name to use as prefix for key description
        """
        super().__init__()
        self.service_name = service_name
        self._keyctl_path = None
        self._keyctl_available = self._check_keyctl_available()

    def _check_keyctl_available(self) -> bool:
        """Check if keyctl utility is available.

        Returns:
            True if keyctl is available, False otherwise
        """
        self._keyctl_path = shutil.which("keyctl")
        if self._keyctl_path is None:
            self._logger.error(
                "keyctl utility not found. Please install keyutils package. "
                "Credential storage in kernel keyring will not be available."
            )
            return False
        self._logger.debug(f"keyctl utility found at: {self._keyctl_path}")
        return True

    def _get_key_description(self, username: str) -> str:
        """Generate key description from service name and username.

        Args:
            username: The username

        Returns:
            The key description string in format "service:username"
        """
        return f"{self.service_name}:{username}"

    def get_password(self, username: str) -> str | None:
        """Retrieve password from kernel keyring.

        Args:
            username: The username for which to retrieve the password

        Returns:
            The password if found, None otherwise
        """
        if not username:
            self._logger.debug("No username provided for password retrieval")
            return None

        if not self._keyctl_available:
            self._logger.error(
                "Cannot retrieve password: keyctl utility is not available"
            )
            return None

        key_description = self._get_key_description(username)
        try:
            # Request the key and get its ID
            result = subprocess.run(
                [self._keyctl_path, "request", "user", key_description],
                capture_output=True,
                text=True,
                check=True,
            )
            key_id = result.stdout.strip()

            # Read the key value
            result = subprocess.run(
                [self._keyctl_path, "pipe", key_id],
                capture_output=True,
                text=True,
                check=True,
            )
            self._logger.debug(
                f"Successfully retrieved password for user '{username}' "
                f"from kernel keyring"
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            # Key not found or other error
            self._logger.debug(
                f"Password not found in kernel keyring for user "
                f"'{username}': {e.stderr}"
            )
            return None
        except FileNotFoundError:
            # keyctl utility not installed (shouldn't happen if
            # _keyctl_available is True)
            self._logger.error(
                "keyctl utility not found despite availability check"
            )
            return None

    def set_password(self, username: str, password: str) -> None:
        """Store password in kernel keyring.

        Args:
            username: The username for which to store the password
            password: The password to store

        Raises:
            KeyringNotFoundError: If keyctl utility is not available
            KeyringOperationError: If keyctl fails to store the password
        """
        if not username or not password:
            self._logger.error(
                "Username and password are required for password storage"
            )
            raise KeyringOperationError("Username and password are required")

        if not self._keyctl_available:
            self._logger.error(
                "Cannot store password: keyctl utility is not available. "
                "Please install keyutils package."
            )
            raise KeyringNotFoundError(
                "keyctl utility not found. Please install keyutils package."
            )

        key_description = self._get_key_description(username)
        try:
            # Add/update the key in the user keyring (@u)
            subprocess.run(
                [self._keyctl_path, "padd", "user", key_description, KEYRING],
                input=password,
                text=True,
                check=True,
                capture_output=True,
            )
            self._logger.info(
                f"Successfully stored password for user '{username}' "
                f"in kernel keyring"
            )
        except FileNotFoundError as e:
            self._logger.error(
                "keyctl utility not found despite availability check"
            )
            raise KeyringNotFoundError(
                "keyctl utility not found. Please install keyutils package.",
            ) from e
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            self._logger.error(
                f"Failed to store password in kernel keyring for user "
                f"'{username}': {error_msg}"
            )
            raise KeyringOperationError(
                f"Failed to store password in kernel keyring: {error_msg}",
            ) from e

    def delete_password(self, username: str) -> bool:
        """Delete password from kernel keyring.

        Args:
            username: The username for which to delete the password

        Returns:
            True if the password was deleted, False if it didn't exist
        """
        if not username:
            self._logger.debug("No username provided for password deletion")
            return False

        if not self._keyctl_available:
            self._logger.error(
                "Cannot delete password: keyctl utility is not available"
            )
            return False

        key_description = self._get_key_description(username)
        try:
            # Request the key to get its ID
            result = subprocess.run(
                [self._keyctl_path, "request", "user", key_description],
                capture_output=True,
                text=True,
                check=True,
            )
            key_id = result.stdout.strip()

            # Unlink/delete the key
            subprocess.run(
                [self._keyctl_path, "unlink", key_id, KEYRING],
                capture_output=True,
                text=True,
                check=True,
            )
            self._logger.info(
                f"Successfully deleted password for user '{username}' "
                f"from kernel keyring"
            )
            return True
        except subprocess.CalledProcessError as e:
            self._logger.debug(
                f"Failed to delete password for user '{username}': {e.stderr}"
            )
            return False
        except FileNotFoundError:
            self._logger.error(
                "keyctl utility not found despite availability check"
            )
            return False
