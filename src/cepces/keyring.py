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
from typing import Dict, Optional  # Python 3.9 compatibility

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

    def is_supported(self) -> bool:
        """Check if kernel keyring is supported on this system.

        Returns:
            True if keyctl utility is available and user keyring is accessible,
            False otherwise
        """
        if not self._keyctl_available:
            return False

        try:
            subprocess.run(
                [self._keyctl_path, "show", KEYRING],
                capture_output=True,
                text=True,
                check=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _get_key_description(self, username: str) -> str:
        """Generate key description from service name and username.

        Args:
            username: The username

        Returns:
            The key description string in format "service:username"
        """
        return f"{self.service_name}:{username}"

    # Using typing.Optional for Python 3.9 compatibility (| operator requires 3.10+)
    def get_password(self, username: str) -> Optional[str]:
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

    # Using typing.Dict and typing.Optional for Python 3.9 compatibility (dict[] and | require 3.10+)
    def dump_key(self, username: str) -> Optional[Dict[str, str]]:
        """Dump key information from kernel keyring for debugging.

        Args:
            username: The username for which to dump key information

        Returns:
            Dictionary containing key metadata if found, None otherwise.
            The dictionary contains: key_id, key_type, uid, gid, perms, description
        """
        if not username:
            self._logger.debug("No username provided for key dump")
            return None

        if not self._keyctl_available:
            self._logger.error(
                "Cannot dump key: keyctl utility is not available"
            )
            return None

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

            # Describe the key to get metadata
            result = subprocess.run(
                [self._keyctl_path, "describe", key_id],
                capture_output=True,
                text=True,
                check=True,
            )

            # Parse the describe output format:
            # KEY_ID: PERMISSIONS  UID  GID TYPE: DESCRIPTION
            # Example: 123456: alswrv-----v------------  1000  1000 user: test:desc
            output = result.stdout.strip()

            # Split on first colon to separate key_id from the rest
            if ": " not in output:
                self._logger.warning(
                    f"Unexpected describe output format for user '{username}': {output}"
                )
                return None

            _, rest = output.split(": ", 1)

            # Split the rest on whitespace and handle type:description
            parts = rest.split()
            if len(parts) >= 4:
                perms = parts[0]
                uid = parts[1]
                gid = parts[2]
                # The rest is "type: description", rejoin everything after gid
                type_and_desc = " ".join(parts[3:])

                # Split type and description on the last occurrence of ": "
                if ": " in type_and_desc:
                    key_type, description = type_and_desc.split(": ", 1)
                else:
                    key_type = type_and_desc
                    description = ""

                key_info = {
                    "key_id": key_id,
                    "key_type": key_type,
                    "uid": uid,
                    "gid": gid,
                    "perms": perms,
                    "description": description,
                }
                self._logger.debug(
                    f"Successfully dumped key information for user '{username}'"
                )
                return key_info

            self._logger.warning(
                f"Unexpected describe output format for user '{username}': {output}"
            )
            return None
        except subprocess.CalledProcessError as e:
            self._logger.debug(
                f"Failed to dump key for user '{username}': {e.stderr}"
            )
            return None
        except FileNotFoundError:
            self._logger.error(
                "keyctl utility not found despite availability check"
            )
            return None
