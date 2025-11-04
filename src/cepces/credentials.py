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
"""Module for handling credential prompting via pinentry utility."""
import shutil
import subprocess
from typing import Dict, List, Optional, Tuple  # Python 3.9 compatibility

from cepces import Base


class CredentialsError(Exception):
    """Base exception for credential operations."""


class CredentialsNotFoundError(CredentialsError):
    """Exception raised when pinentry utility is not found."""


class CredentialsOperationError(CredentialsError):
    """Exception raised when credential prompt operation fails."""


class CredentialsHandler(Base):
    """Handler for credential prompting using pinentry utility."""

    def __init__(self, title: str = "Authentication Required"):
        """Initialize the CredentialsHandler.

        Args:
            title: The title to display in the pinentry dialog
        """
        super().__init__()
        self.title = title
        self._pinentry_path = None
        self._pinentry_available = self._check_pinentry_available()

    def _check_pinentry_available(self) -> bool:
        """Check if pinentry utility is available.

        Returns:
            True if pinentry is available, False otherwise
        """
        self._pinentry_path = shutil.which("pinentry")
        if self._pinentry_path is None:
            self._logger.error(
                "pinentry utility not found. Please install pinentry package. "
                "Interactive credential prompting will not be available."
            )
            return False
        self._logger.debug(f"pinentry utility found at: {self._pinentry_path}")
        return True

    def is_supported(self) -> bool:
        """Check if pinentry is supported on this system.

        Returns:
            True if pinentry utility is available, False otherwise
        """
        return self._pinentry_available

    # Using typing.List and typing.Dict for Python 3.9 compatibility (| and list[]/dict[] require 3.10+)
    def _run_pinentry(self, commands: List[str]) -> Dict[str, str]:
        """Run pinentry with the given commands.

        Args:
            commands: List of pinentry commands to execute

        Returns:
            Dictionary with parsed responses from pinentry

        Raises:
            CredentialsOperationError: If pinentry execution fails
        """
        if not self._pinentry_available:
            raise CredentialsNotFoundError(
                "pinentry utility not found. Please install pinentry package."
            )

        try:
            # Join commands with newlines and add BYE at the end
            input_data = "\n".join(commands + ["BYE"]) + "\n"

            result = subprocess.run(
                [self._pinentry_path],
                input=input_data,
                capture_output=True,
                text=True,
                check=False,
            )

            # Parse the output
            responses = {}
            for line in result.stdout.splitlines():
                if line.startswith("D "):
                    # Data response - contains the actual value
                    responses["data"] = line[2:]
                elif line.startswith("OK"):
                    responses["ok"] = True
                elif line.startswith("ERR"):
                    responses["error"] = (
                        line[4:] if len(line) > 4 else "Unknown error"
                    )

            return responses
        except FileNotFoundError as e:
            raise CredentialsNotFoundError(
                "pinentry utility not found. Please install pinentry package."
            ) from e
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            raise CredentialsOperationError(
                f"Failed to run pinentry: {error_msg}"
            ) from e

    # Using typing.Optional for Python 3.9 compatibility (| operator requires 3.10+)
    def prompt_password(
        self,
        description: str = "Enter your password",
        prompt: str = "Password:",
    ) -> Optional[str]:
        """Prompt user for a password using pinentry.

        Args:
            description: Description text to display in the dialog
            prompt: Prompt text for the password field

        Returns:
            The password entered by the user, or None if cancelled
        """
        if not self._pinentry_available:
            self._logger.error(
                "Cannot prompt for password: pinentry utility is not available"
            )
            return None

        commands = [
            f"SETTITLE {self.title}",
            f"SETDESC {description}",
            f"SETPROMPT {prompt}",
            "GETPIN",
        ]

        try:
            responses = self._run_pinentry(commands)

            if "error" in responses:
                self._logger.debug(
                    f"User cancelled password prompt or error occurred: "
                    f"{responses.get('error')}"
                )
                return None

            if "data" in responses:
                self._logger.debug("Successfully obtained password from user")
                return responses["data"]

            self._logger.debug("No password data returned from pinentry")
            return None

        except CredentialsError as e:
            self._logger.error(f"Failed to prompt for password: {e}")
            return None

    # Using typing.Tuple and typing.Optional for Python 3.9 compatibility (tuple[] and | require 3.10+)
    def prompt_credentials(
        self,
        username_description: str = "Enter your username",
        password_description: str = "Enter your password",
    ) -> Tuple[Optional[str], Optional[str]]:
        """Prompt user for both username and password using pinentry.

        Args:
            username_description: Description for the username prompt
            password_description: Description for the password prompt

        Returns:
            Tuple of (username, password), or (None, None) if cancelled
        """
        if not self._pinentry_available:
            self._logger.error(
                "Cannot prompt for credentials: pinentry utility is not available"
            )
            return None, None

        # Prompt for username (using GETPIN without password masking would be ideal,
        # but pinentry doesn't have a direct "get text" command, so we use GETPIN)
        # For better UX, we could call it twice with different descriptions
        username_commands = [
            f"SETTITLE {self.title}",
            f"SETDESC {username_description}",
            "SETPROMPT Username:",
            "GETPIN",
        ]

        try:
            username_responses = self._run_pinentry(username_commands)

            if "error" in username_responses:
                self._logger.debug("User cancelled username prompt")
                return None, None

            username = username_responses.get("data")
            if not username:
                self._logger.debug("No username entered")
                return None, None

            # Now prompt for password
            password = self.prompt_password(
                description=password_description, prompt="Password:"
            )

            if not password:
                self._logger.debug("No password entered")
                return None, None

            self._logger.debug(
                f"Successfully obtained credentials for user '{username}'"
            )
            return username, password

        except CredentialsError as e:
            self._logger.error(f"Failed to prompt for credentials: {e}")
            return None, None
