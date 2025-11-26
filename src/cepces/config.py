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
"""Module handling configuration loading."""
from configparser import ConfigParser, ExtendedInterpolation
from pathlib import Path
import logging
import re
import socket
import os
from cepces import Base
from cepces import auth as CoreAuth
from cepces.soap import auth as SOAPAuth


DEFAULT_CONFIG_FILES = [
    "/etc/cepces/cepces.conf",
    "/usr/local/etc/cepces/cepces.conf",
    "conf/cepces.conf",
    "cepces.conf",
]

DEFAULT_CONFIG_DIRS = [
    "/etc/cepces/conf.d",
    "/usr/local/etc/cepces/conf.d" "conf/conf.d",
]


class Configuration(Base):
    """Base configuration class."""

    AUTH_HANDLER_MAP = {
        "Anonymous": CoreAuth.AnonymousAuthenticationHandler,
        "Kerberos": CoreAuth.GSSAPIAuthenticationHandler,
        "UsernamePassword": CoreAuth.UsernamePasswordAuthenticationHandler,
        "Certificate": CoreAuth.CertificateAuthenticationHandler,
    }

    AUTH_MAP = {
        "Anonymous": SOAPAuth.AnonymousAuthentication,
        "Kerberos": SOAPAuth.TransportGSSAPIAuthentication,
        "UsernamePassword": SOAPAuth.MessageUsernamePasswordAuthentication,
        "Certificate": SOAPAuth.TransportCertificateAuthentication,
    }

    # Regex patterns for display detection
    # Xorg displays start with : and numbers (e.g., :0, :1, :0.0)
    XORG_DISPLAY_PATTERN = re.compile(r"^:[0-9]+(\.[0-9]+)?$")
    # Wayland displays contain "wayland" in the name
    WAYLAND_DISPLAY_PATTERN = re.compile(r"wayland", re.IGNORECASE)

    def __init__(
        self,
        parser,
        endpoint,
        endpoint_type,
        cas,
        auth,
        poll_interval,
        openssl_ciphers,
        display=None,
    ):
        super().__init__()

        self._parser = parser
        self._endpoint = endpoint
        self._endpoint_type = endpoint_type
        self._cas = cas
        self._auth = auth
        self._poll_interval = poll_interval
        self._openssl_ciphers = openssl_ciphers
        self._display = display

    @property
    def parser(self):
        """Return the parser."""
        return self._parser

    @property
    def endpoint(self):
        """Return the endpoint."""
        return self._endpoint

    @property
    def endpoint_type(self):
        """Return the endpoint."""
        return self._endpoint_type

    @property
    def cas(self):
        """Return the CA path."""
        return self._cas

    @property
    def auth(self):
        """Return the authentication method."""
        return self._auth

    @property
    def poll_interval(self):
        """Return the poll interval."""
        return self._poll_interval

    @property
    def openssl_ciphers(self):
        """Return the openssl cipher string."""
        return self._openssl_ciphers

    @property
    def display(self):
        """Return the display setting.

        Returns:
            Tuple of (environment_variable_name, display_value) if
            display is set, otherwise None. The environment variable
            name will be either 'DISPLAY' or 'WAYLAND_DISPLAY' based
            on the display value format.
        """
        if self._display is None or self._display == "":
            return None

        env_var = self._detect_display_type(self._display)
        return (env_var, self._display)

    @staticmethod
    def _detect_display_type(display_value):
        """Detect whether a display value is for Xorg or Wayland.

        Args:
            display_value: The display string to check

        Returns:
            'DISPLAY' for Xorg displays, 'WAYLAND_DISPLAY' for Wayland displays
        """
        if Configuration.XORG_DISPLAY_PATTERN.match(display_value):
            return "DISPLAY"
        if Configuration.WAYLAND_DISPLAY_PATTERN.search(display_value):
            return "WAYLAND_DISPLAY"
        # Default to DISPLAY for unknown formats
        return "DISPLAY"

    def get_user_config(self):
        """Get user certificate configuration.

        Returns:
            UserConfig instance with user certificate settings.

        Raises:
            RuntimeError: If user section is missing or invalid.
        """
        return self._load_user_config(self._parser)

    @staticmethod
    def _load_user_config(parser):
        """Load user certificate configuration from parser."""
        if "user" not in parser:
            return None

        section = parser["user"]

        key_file = os.path.expanduser(section.get("key_file", "~/key.pem"))
        cert_file = os.path.expanduser(section.get("cert_file", "~/cert.pem"))
        req_file = os.path.expanduser(section.get("req_file", "~/cert.req"))
        profile = section.get("profile", "")
        renew_days_str = section.get("renew_days", "30")
        key_size_str = section.get("key_size", "4096")

        try:
            renew_days = int(renew_days_str)
        except (ValueError, TypeError):
            raise RuntimeError(f"Invalid renew_days value: {renew_days_str}")

        try:
            key_size = int(key_size_str)
        except (ValueError, TypeError):
            raise RuntimeError(f"Invalid key_size value: {key_size_str}")

        # Validate required fields
        if not all([key_file, cert_file, req_file, profile]):
            raise RuntimeError(
                "One or more required config options are missing in [user] section: "
                "key_file, cert_file, req_file, profile"
            )

        return key_file, cert_file, req_file, profile, renew_days, key_size

    @classmethod
    def load(
        cls, files=None, dirs=None, global_overrides=None, krb5_overrides=None
    ):
        """Load configuration files and directories and instantiate a new
        Configuration."""
        name = "{}.{}".format(
            cls.__module__,
            cls.__name__,
        )
        logger = logging.getLogger(name)

        logger.debug("Initializing application configuration.")
        config = ConfigParser(interpolation=ExtendedInterpolation())
        # Make options case sensitive
        config.optionxform = str  # type: ignore[method-assign,assignment]

        # Add some defaults.
        hostname = socket.gethostname().lower()
        fqdn = socket.getfqdn()
        shortname = hostname.split(".")[0]

        config["DEFAULT"]["hostname"] = hostname.lower()
        config["DEFAULT"]["HOSTNAME"] = hostname.upper()
        config["DEFAULT"]["fqdn"] = fqdn.lower()
        config["DEFAULT"]["FQDN"] = fqdn.upper()
        config["DEFAULT"]["shortname"] = shortname.lower()
        config["DEFAULT"]["SHORTNAME"] = shortname.upper()

        if not config.has_section("global"):
            config.add_section("global")
        config["global"]["openssl_ciphers"] = ""

        if files is None:
            files = DEFAULT_CONFIG_FILES

        if dirs is None:
            dirs = DEFAULT_CONFIG_DIRS

        # Read all configuration files.
        for path in [Path(x) for x in files]:
            if path.is_file():
                logger.debug("Reading: {0:s}".format(path.__str__()))
                config.read(path.__str__())

        # Read all configuration directories.
        for cdir in [Path(x) for x in dirs]:
            if cdir.is_dir():
                for path in sorted([x for x in cdir.iterdir() if x.is_file()]):
                    logger.debug("Reading: {0:s}".format(path.__str__()))
                    config.read(path)

        # Override globals set from the command line
        if global_overrides is not None:
            for key, val in global_overrides.items():
                config["global"][key] = val
        if krb5_overrides is not None:
            for key, val in krb5_overrides.items():
                config["kerberos"][key] = val

        return Configuration.from_parser(config)

    @classmethod
    def from_parser(cls, parser):
        """Create a Configuration instance from a ConfigParser."""
        name = "{}.{}".format(
            cls.__module__,
            cls.__name__,
        )
        logger = logging.getLogger(name)

        # Ensure there's a global section present.
        if "global" not in parser:
            raise RuntimeError('Missing "global" section in configuration.')

        section = parser["global"]

        # Ensure certain required variables are present.
        for var in [
            "endpoint",
            "auth",
            "type",
            "poll_interval",
            "openssl_ciphers",
        ]:
            if var not in section:
                raise RuntimeError(
                    'Missing "{}/{}" variable in configuration.'.format(
                        "global",
                        var,
                    ),
                )

        # Verify that the chosen authentication method is valid.
        if section["auth"] not in Configuration.AUTH_HANDLER_MAP.keys():
            raise RuntimeError(
                "No such authentication method: {}".format(
                    section["auth"],
                ),
            )

        # Store the global configuration options.
        endpoint = section.get("endpoint")
        endpoint_type = section.get("type")
        authn = Configuration.AUTH_HANDLER_MAP[section["auth"]](parser)  # type: ignore[abstract]  # noqa: E501
        cas = section.get("cas", True)
        poll_interval = section.get("poll_interval")
        openssl_ciphers = section.get("openssl_ciphers")
        display = section.get("display", None)

        # Warn if deprecated openssl_seclevel is still set
        if "openssl_seclevel" in section:
            logger.warning(
                "The 'openssl_seclevel' configuration option is deprecated. "
                "Please use 'openssl_ciphers' instead (e.g., "
                "'openssl_ciphers=DEFAULT:@SECLEVEL=1')."
            )

        if cas == "":
            cas = False

        return Configuration(
            parser,
            endpoint,
            endpoint_type,
            cas,
            authn.handle(),
            poll_interval,
            openssl_ciphers,
            display,
        )
