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
"""Module for handling credential prompting via multiple backends.

Supports pinentry, kdialog, and zenity utilities with automatic fallback.
"""
import os
import shutil
import subprocess
from typing import Dict, List, Optional, Tuple  # Python 3.9 compatibility

from cepces import Base


def get_env_with_display(
    display_config: Optional[Tuple[str, str]] = None,
) -> dict:
    """Get environment dict with display variable set if configured.

    Args:
        display_config: Optional tuple of (env_var_name,
            display_value) from configuration

    Returns:
        Environment dictionary with display settings
    """
    env = os.environ.copy()
    if display_config is not None:
        env_var, display_value = display_config
        env[env_var] = display_value
    return env


class CredentialsError(Exception):
    """Base exception for credential operations."""


class CredentialsNotFoundError(CredentialsError):
    """Exception raised when pinentry utility is not found."""


class CredentialsOperationError(CredentialsError):
    """Exception raised when credential prompt operation fails."""


class PinentryHandler(Base):
    """Handler for credential prompting using pinentry utility."""

    def __init__(self, title: str = "Authentication Required"):
        """Initialize the PinentryHandler.

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

    # Using typing.List and typing.Dict for Python 3.9 compatibility
    # (| and list[]/dict[] require 3.10+)
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

    # Using typing.Optional for Python 3.9 compatibility
    # (| operator requires 3.10+)
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

    # Using typing.Tuple and typing.Optional for Python 3.9 compatibility
    # (tuple[] and | require 3.10+)
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
                "Cannot prompt for credentials: "
                "pinentry utility is not available"
            )
            return None, None

        # Prompt for username (using GETPIN without password masking
        # would be ideal, but pinentry doesn't have a direct
        # "get text" command, so we use GETPIN)
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


class KdialogHandler(Base):
    """Handler for credential prompting using kdialog utility."""

    def __init__(
        self,
        title: str = "Authentication Required",
        display_config: Optional[tuple] = None,
    ):
        """Initialize the KdialogHandler.

        Args:
            title: The title to display in the kdialog dialog
            display_config: Optional tuple of (env_var_name,
                display_value) from configuration
        """
        super().__init__()
        self.title = title
        self._display_config = display_config
        self._kdialog_path = None
        self._kdialog_available = self._check_kdialog_available()

    def _check_kdialog_available(self) -> bool:
        """Check if kdialog utility is available.

        Returns:
            True if kdialog is available, False otherwise
        """
        self._kdialog_path = shutil.which("kdialog")
        if self._kdialog_path is None:
            self._logger.debug(
                "kdialog utility not found. "
                "KDE credential prompting will not be available."
            )
            return False

        # Check if running in a graphical environment
        # Use configured display if available, otherwise check environment
        if self._display_config is None:
            if not os.environ.get("DISPLAY") and not os.environ.get(
                "WAYLAND_DISPLAY"
            ):
                self._logger.debug(
                    "kdialog found but no DISPLAY or WAYLAND_DISPLAY set. "
                    "KDE credential prompting will not be available."
                )
                return False
        else:
            self._logger.debug(
                f"Using configured display: "
                f"{self._display_config[0]}={self._display_config[1]}"
            )

        self._logger.debug(f"kdialog utility found at: {self._kdialog_path}")
        return True

    def is_supported(self) -> bool:
        """Check if kdialog is supported on this system.

        Returns:
            True if kdialog utility is available, False otherwise
        """
        return self._kdialog_available

    def prompt_password(
        self,
        description: str = "Enter your password",
        prompt: str = "Password:",
    ) -> Optional[str]:
        """Prompt user for a password using kdialog.

        Args:
            description: Description text to display in the dialog
            prompt: Prompt text for the password field (unused by kdialog)

        Returns:
            The password entered by the user, or None if cancelled
        """
        if not self._kdialog_available:
            self._logger.error(
                "Cannot prompt for password: "
                "kdialog utility is not available"
            )
            return None

        try:
            result = subprocess.run(
                [
                    self._kdialog_path,
                    "--title",
                    self.title,
                    "--password",
                    description,
                ],
                capture_output=True,
                text=True,
                check=False,
                env=get_env_with_display(self._display_config),
            )

            if result.returncode == 0:
                password = result.stdout.strip()
                self._logger.debug("Successfully obtained password from user")
                return password

            self._logger.debug("User cancelled password prompt")
            return None

        except Exception as e:
            self._logger.error(f"Failed to prompt for password: {e}")
            return None

    def prompt_credentials(
        self,
        username_description: str = "Enter your username",
        password_description: str = "Enter your password",
    ) -> Tuple[Optional[str], Optional[str]]:
        """Prompt user for both username and password using kdialog.

        Args:
            username_description: Description for the username prompt
            password_description: Description for the password prompt

        Returns:
            Tuple of (username, password), or (None, None) if cancelled
        """
        if not self._kdialog_available:
            self._logger.error(
                "Cannot prompt for credentials: "
                "kdialog utility is not available"
            )
            return None, None

        try:
            # Prompt for username
            username_result = subprocess.run(
                [
                    self._kdialog_path,
                    "--title",
                    self.title,
                    "--inputbox",
                    username_description,
                ],
                capture_output=True,
                text=True,
                check=False,
                env=get_env_with_display(self._display_config),
            )

            if username_result.returncode != 0:
                self._logger.debug("User cancelled username prompt")
                return None, None

            username = username_result.stdout.strip()
            if not username:
                self._logger.debug("No username entered")
                return None, None

            # Prompt for password
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

        except Exception as e:
            self._logger.error(f"Failed to prompt for credentials: {e}")
            return None, None


class ZenityHandler(Base):
    """Handler for credential prompting using zenity utility."""

    def __init__(
        self,
        title: str = "Authentication Required",
        display_config: Optional[tuple] = None,
    ):
        """Initialize the ZenityHandler.

        Args:
            title: The title to display in the zenity dialog
            display_config: Optional tuple of (env_var_name,
                display_value) from configuration
        """
        super().__init__()
        self.title = title
        self._display_config = display_config
        self._zenity_path = None
        self._zenity_available = self._check_zenity_available()

    def _check_zenity_available(self) -> bool:
        """Check if zenity utility is available.

        Returns:
            True if zenity is available, False otherwise
        """
        self._zenity_path = shutil.which("zenity")
        if self._zenity_path is None:
            self._logger.debug(
                "zenity utility not found. "
                "GNOME credential prompting will not be available."
            )
            return False

        # Check if running in a graphical environment
        # Use configured display if available, otherwise check environment
        if self._display_config is None:
            if not os.environ.get("DISPLAY") and not os.environ.get(
                "WAYLAND_DISPLAY"
            ):
                self._logger.debug(
                    "zenity found but no DISPLAY or WAYLAND_DISPLAY set. "
                    "GNOME credential prompting will not be available."
                )
                return False
        else:
            self._logger.debug(
                f"Using configured display: "
                f"{self._display_config[0]}={self._display_config[1]}"
            )

        self._logger.debug(f"zenity utility found at: {self._zenity_path}")
        return True

    def is_supported(self) -> bool:
        """Check if zenity is supported on this system.

        Returns:
            True if zenity utility is available, False otherwise
        """
        return self._zenity_available

    def prompt_password(
        self,
        description: str = "Enter your password",
        prompt: str = "Password:",
    ) -> Optional[str]:
        """Prompt user for a password using zenity.

        Args:
            description: Description text to display in the dialog
            prompt: Prompt text for the password field (unused by zenity)

        Returns:
            The password entered by the user, or None if cancelled
        """
        if not self._zenity_available:
            self._logger.error(
                "Cannot prompt for password: zenity not available"
            )
            return None

        try:
            result = subprocess.run(
                [
                    self._zenity_path,
                    "--password",
                    "--title",
                    self.title,
                    "--text",
                    description,
                ],
                capture_output=True,
                text=True,
                check=False,
                env=get_env_with_display(self._display_config),
            )

            if result.returncode == 0:
                password = result.stdout.strip()
                self._logger.debug("Successfully obtained password from user")
                return password

            self._logger.debug("User cancelled password prompt")
            return None

        except Exception as e:
            self._logger.error(f"Failed to prompt for password: {e}")
            return None

    def prompt_credentials(
        self,
        username_description: str = "Enter your username",
        password_description: str = "Enter your password",
    ) -> Tuple[Optional[str], Optional[str]]:
        """Prompt user for both username and password using zenity.

        Args:
            username_description: Description for the username prompt
            password_description: Description for the password prompt

        Returns:
            Tuple of (username, password), or (None, None) if cancelled
        """
        if not self._zenity_available:
            self._logger.error(
                "Cannot prompt for credentials: "
                "zenity utility is not available"
            )
            return None, None

        try:
            # Prompt for username
            username_result = subprocess.run(
                [
                    self._zenity_path,
                    "--entry",
                    "--title",
                    self.title,
                    "--text",
                    username_description,
                ],
                capture_output=True,
                text=True,
                check=False,
                env=get_env_with_display(self._display_config),
            )

            if username_result.returncode != 0:
                self._logger.debug("User cancelled username prompt")
                return None, None

            username = username_result.stdout.strip()
            if not username:
                self._logger.debug("No username entered")
                return None, None

            # Prompt for password
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

        except Exception as e:
            self._logger.error(f"Failed to prompt for credentials: {e}")
            return None, None


class CredentialsHandler(Base):
    """Handler for credential operations with multiple backend support.

    This class provides a flexible interface for credential handling that
    tries multiple backends in order: pinentry, kdialog, zenity.
    """

    def __init__(
        self,
        title: str = "Authentication Required",
        display_config: Optional[Tuple[str, str]] = None,
    ):
        """Initialize the CredentialsHandler.

        Args:
            title: The title to display in credential prompts
            display_config: Optional tuple of (env_var_name,
                display_value) from configuration
        """
        super().__init__()
        self._title = title
        self._display_config = display_config
        self._pinentry_handler = PinentryHandler(title=title)
        self._kdialog_handler = KdialogHandler(
            title=title, display_config=display_config
        )
        self._zenity_handler = ZenityHandler(
            title=title, display_config=display_config
        )
        self._active_handler = self._select_handler()

    def _select_handler(self) -> Optional[Base]:
        """Select the first available credential handler.

        Tries handlers in this order:
        1. pinentry (always preferred if available)
        2. kdialog (if KDE_FULL_SESSION is set and kdialog available)
        3. zenity (if kdialog not preferred or unavailable)

        Returns:
            The first available handler, or None if none are available
        """
        # pinentry is always preferred if available
        if self._pinentry_handler.is_supported():
            self._logger.debug("Using pinentry for credential prompting")
            return self._pinentry_handler

        # Check if running in KDE session
        in_kde_session = bool(os.environ.get("KDE_FULL_SESSION"))

        if in_kde_session:
            # Prefer kdialog in KDE session
            if self._kdialog_handler.is_supported():
                self._logger.debug(
                    "Using kdialog for credential prompting (KDE session)"
                )
                return self._kdialog_handler
            if self._zenity_handler.is_supported():
                self._logger.debug(
                    "Using zenity for credential prompting "
                    "(KDE session but kdialog unavailable)"
                )
                return self._zenity_handler
        else:
            # Prefer zenity in non-KDE sessions
            if self._zenity_handler.is_supported():
                self._logger.debug("Using zenity for credential prompting")
                return self._zenity_handler
            if self._kdialog_handler.is_supported():
                self._logger.debug(
                    "Using kdialog for credential prompting "
                    "(zenity unavailable)"
                )
                return self._kdialog_handler

        self._logger.warning(
            "No credential prompting utilities found. "
            "Please install pinentry, kdialog, or zenity."
        )
        return None

    @property
    def title(self) -> str:
        """Get the title used for credential prompts."""
        return self._title

    @property
    def _pinentry_available(self) -> bool:
        """Check if pinentry utility is available.

        This property is maintained for backward compatibility with tests.
        """
        return self._pinentry_handler._pinentry_available

    def _run_pinentry(self, commands: List[str]) -> Dict[str, str]:
        """Run pinentry with the given commands.

        This method is maintained for backward compatibility with tests.

        Args:
            commands: List of pinentry commands to execute

        Returns:
            Dictionary with parsed responses from pinentry

        Raises:
            CredentialsOperationError: If pinentry execution fails
        """
        return self._pinentry_handler._run_pinentry(commands)

    def is_supported(self) -> bool:
        """Check if credential prompting is supported on this system.

        Returns:
            True if any credential prompting utility is available
        """
        return self._active_handler is not None

    def prompt_password(
        self,
        description: str = "Enter your password",
        prompt: str = "Password:",
    ) -> Optional[str]:
        """Prompt user for a password.

        Args:
            description: Description text to display in the dialog
            prompt: Prompt text for the password field

        Returns:
            The password entered by the user, or None if cancelled
        """
        if self._active_handler is None:
            self._logger.error(
                "Cannot prompt for password: "
                "no credential prompting utility is available"
            )
            return None
        return self._active_handler.prompt_password(description, prompt)

    def prompt_credentials(
        self,
        username_description: str = "Enter your username",
        password_description: str = "Enter your password",
    ) -> Tuple[Optional[str], Optional[str]]:
        """Prompt user for both username and password.

        Args:
            username_description: Description for the username prompt
            password_description: Description for the password prompt

        Returns:
            Tuple of (username, password), or (None, None) if cancelled
        """
        if self._active_handler is None:
            self._logger.error(
                "Cannot prompt for credentials: "
                "no credential prompting utility is available"
            )
            return None, None
        return self._active_handler.prompt_credentials(
            username_description, password_description
        )
