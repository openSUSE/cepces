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
from abc import ABC, abstractmethod

from cepces import Base


class CredentialsError(Exception):
    """Base exception for credential operations."""


class CredentialsNotFoundError(CredentialsError):
    """Exception raised when pinentry utility is not found."""


class CredentialsOperationError(CredentialsError):
    """Exception raised when credential prompt operation fails."""


class CredentialBackend(Base, ABC):
    """Abstract base class for credential prompting backends.

    Provides common functionality for checking utility availability,
    display environment validation, and template methods for credential
    prompting workflows.
    """

    def __init__(
        self,
        title: str = "Authentication Required",
        display_config: tuple[str, str] | None = None,
    ):
        """Initialize the credential backend.

        Args:
            title: The title to display in credential prompts
            display_config: Optional tuple of (env_var_name,
                display_value) from configuration
        """
        super().__init__()
        self.title = title
        self._display_config = display_config
        self._utility_path = None
        self._utility_available = self._check_utility_available()

    def _get_env_with_display(self) -> dict:
        """Get environment dict with display variable set if configured.

        Returns:
            Environment dictionary with display settings
        """
        env = os.environ.copy()
        if self._display_config is not None:
            env_var, display_value = self._display_config
            env[env_var] = display_value
        return env

    @abstractmethod
    def _get_utility_name(self) -> str:
        """Get the name of the utility used by this backend.

        Returns:
            The name of the utility (e.g., "pinentry", "kdialog", "zenity")
        """

    @abstractmethod
    def _requires_display(self) -> bool:
        """Check if this backend requires a display environment.

        Returns:
            True if the backend requires DISPLAY or WAYLAND_DISPLAY
        """

    @abstractmethod
    def _prompt_username(self, description: str) -> str | None:
        """Prompt user for a username.

        Args:
            description: Description text to display in the dialog

        Returns:
            The username entered by the user, or None if cancelled
        """

    @abstractmethod
    def prompt_password(
        self,
        description: str = "Enter your password",
        prompt: str = "Password:",
    ) -> str | None:
        """Prompt user for a password.

        Args:
            description: Description text to display in the dialog
            prompt: Prompt text for the password field

        Returns:
            The password entered by the user, or None if cancelled
        """

    def _check_display_available(self) -> bool:
        """Check if display environment is available.

        Returns:
            True if display is configured or environment variables are set
        """
        # Use configured display if available
        if self._display_config is not None:
            self._logger.debug(
                f"Using configured display: "
                f"{self._display_config[0]}={self._display_config[1]}"
            )
            return True

        # Check environment variables
        if not os.environ.get("DISPLAY") and not os.environ.get(
            "WAYLAND_DISPLAY"
        ):
            utility_name = self._get_utility_name()
            self._logger.debug(
                f"{utility_name} found but no DISPLAY or WAYLAND_DISPLAY set. "
                f"Credential prompting will not be available."
            )
            return False

        return True

    def _check_utility_available(self) -> bool:
        """Check if the utility is available on the system.

        Returns:
            True if utility is available and requirements are met
        """
        utility_name = self._get_utility_name()
        self._utility_path = shutil.which(utility_name)

        if self._utility_path is None:
            log_level = "error" if utility_name == "pinentry" else "debug"
            log_msg = (
                f"{utility_name} utility not found. "
                f"Please install {utility_name} package. "
                if utility_name == "pinentry"
                else f"{utility_name} utility not found. "
            )
            log_msg += (
                "Interactive credential prompting will not be available."
                if utility_name == "pinentry"
                else "Credential prompting will not be available."
            )

            if log_level == "error":
                self._logger.error(log_msg)
            else:
                self._logger.debug(log_msg)
            return False

        self._logger.debug(
            f"{utility_name} utility found at: {self._utility_path}"
        )

        # Check display requirements
        if self._requires_display() and not self._check_display_available():
            return False

        return True

    def is_supported(self) -> bool:
        """Check if this backend is supported on this system.

        Returns:
            True if utility is available and requirements are met
        """
        return self._utility_available

    def prompt_credentials(
        self,
        username_description: str = "Enter your username",
        password_description: str = "Enter your password",
    ) -> tuple[str | None, str | None]:
        """Prompt user for both username and password.

        This is a template method that handles the common workflow.

        Args:
            username_description: Description for the username prompt
            password_description: Description for the password prompt

        Returns:
            Tuple of (username, password), or (None, None) if cancelled
        """
        if not self._utility_available:
            utility_name = self._get_utility_name()
            self._logger.error(
                f"Cannot prompt for credentials: "
                f"{utility_name} utility is not available"
            )
            return None, None

        try:
            # Prompt for username
            username = self._prompt_username(username_description)

            if not username:
                self._logger.debug(
                    "User cancelled username prompt or no username entered"
                )
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


class PinentryBackend(CredentialBackend):
    """Backend for credential prompting using pinentry utility."""

    def __init__(self, title: str = "Authentication Required"):
        """Initialize the PinentryBackend.

        Args:
            title: The title to display in the pinentry dialog
        """
        super().__init__(title=title, display_config=None)
        # Maintain backward compatibility
        self._pinentry_path = self._utility_path
        self._pinentry_available = self._utility_available

    def _get_utility_name(self) -> str:
        """Get the name of the utility used by this backend.

        Returns:
            The name of the utility
        """
        return "pinentry"

    def _requires_display(self) -> bool:
        """Check if this backend requires a display environment.

        Returns:
            False - pinentry doesn't require DISPLAY environment
        """
        return False

    def _run_pinentry(self, commands: list[str]) -> dict[str, str]:
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

    def _prompt_username(self, description: str) -> str | None:
        """Prompt user for a username using pinentry.

        Args:
            description: Description text to display in the dialog

        Returns:
            The username entered by the user, or None if cancelled
        """
        # Prompt for username (using GETPIN without password masking
        # would be ideal, but pinentry doesn't have a direct
        # "get text" command, so we use GETPIN)
        username_commands = [
            f"SETTITLE {self.title}",
            f"SETDESC {description}",
            "SETPROMPT Username:",
            "GETPIN",
        ]

        try:
            username_responses = self._run_pinentry(username_commands)

            if "error" in username_responses:
                self._logger.debug("User cancelled username prompt")
                return None

            return username_responses.get("data")

        except CredentialsError as e:
            self._logger.error(f"Failed to prompt for username: {e}")
            return None

    def prompt_password(
        self,
        description: str = "Enter your password",
        prompt: str = "Password:",
    ) -> str | None:
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


class KdialogBackend(CredentialBackend):
    """Backend for credential prompting using kdialog utility."""

    def __init__(
        self,
        title: str = "Authentication Required",
        display_config: tuple | None = None,
    ):
        """Initialize the KdialogBackend.

        Args:
            title: The title to display in the kdialog dialog
            display_config: Optional tuple of (env_var_name,
                display_value) from configuration
        """
        super().__init__(title=title, display_config=display_config)
        # Maintain backward compatibility
        self._kdialog_path = self._utility_path
        self._kdialog_available = self._utility_available

    def _get_utility_name(self) -> str:
        """Get the name of the utility used by this backend.

        Returns:
            The name of the utility
        """
        return "kdialog"

    def _requires_display(self) -> bool:
        """Check if this backend requires a display environment.

        Returns:
            True - kdialog requires DISPLAY or WAYLAND_DISPLAY
        """
        return True

    def _prompt_username(self, description: str) -> str | None:
        """Prompt user for a username using kdialog.

        Args:
            description: Description text to display in the dialog

        Returns:
            The username entered by the user, or None if cancelled
        """
        try:
            username_result = subprocess.run(
                [
                    self._kdialog_path,
                    "--title",
                    self.title,
                    "--inputbox",
                    description,
                ],
                capture_output=True,
                text=True,
                check=False,
                env=self._get_env_with_display(),
            )

            if username_result.returncode != 0:
                self._logger.debug("User cancelled username prompt")
                return None

            username = username_result.stdout.strip()
            return username if username else None

        except Exception as e:
            self._logger.error(f"Failed to prompt for username: {e}")
            return None

    def prompt_password(
        self,
        description: str = "Enter your password",
        prompt: str = "Password:",
    ) -> str | None:
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
                env=self._get_env_with_display(),
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


class ZenityBackend(CredentialBackend):
    """Backend for credential prompting using zenity utility."""

    def __init__(
        self,
        title: str = "Authentication Required",
        display_config: tuple | None = None,
    ):
        """Initialize the ZenityBackend.

        Args:
            title: The title to display in the zenity dialog
            display_config: Optional tuple of (env_var_name,
                display_value) from configuration
        """
        super().__init__(title=title, display_config=display_config)
        # Maintain backward compatibility
        self._zenity_path = self._utility_path
        self._zenity_available = self._utility_available

    def _get_utility_name(self) -> str:
        """Get the name of the utility used by this backend.

        Returns:
            The name of the utility
        """
        return "zenity"

    def _requires_display(self) -> bool:
        """Check if this backend requires a display environment.

        Returns:
            True - zenity requires DISPLAY or WAYLAND_DISPLAY
        """
        return True

    def _prompt_username(self, description: str) -> str | None:
        """Prompt user for a username using zenity.

        Args:
            description: Description text to display in the dialog

        Returns:
            The username entered by the user, or None if cancelled
        """
        try:
            username_result = subprocess.run(
                [
                    self._zenity_path,
                    "--entry",
                    "--title",
                    self.title,
                    "--text",
                    description,
                ],
                capture_output=True,
                text=True,
                check=False,
                env=self._get_env_with_display(),
            )

            if username_result.returncode != 0:
                self._logger.debug("User cancelled username prompt")
                return None

            username = username_result.stdout.strip()
            return username if username else None

        except Exception as e:
            self._logger.error(f"Failed to prompt for username: {e}")
            return None

    def prompt_password(
        self,
        description: str = "Enter your password",
        prompt: str = "Password:",
    ) -> str | None:
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
                env=self._get_env_with_display(),
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


class CredentialsHandler(Base):
    """Handler for credential operations with multiple backend support.

    This class provides a flexible interface for credential handling that
    tries multiple backends in order: pinentry, kdialog, zenity.
    """

    def __init__(
        self,
        title: str = "Authentication Required",
        display_config: tuple[str, str] | None = None,
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
        self._pinentry_handler = PinentryBackend(title=title)
        self._kdialog_handler = KdialogBackend(
            title=title, display_config=display_config
        )
        self._zenity_handler = ZenityBackend(
            title=title, display_config=display_config
        )
        self._active_handler = self._select_handler()

    def _select_handler(self) -> Base | None:
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

    def _run_pinentry(self, commands: list[str]) -> dict[str, str]:
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
    ) -> str | None:
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
    ) -> tuple[str | None, str | None]:
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
