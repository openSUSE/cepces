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
"""Module for HTTP/HTTPS session configuration with SSL support."""

import ssl
from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context


class SSLAdapter(HTTPAdapter):
    """Custom HTTPAdapter that allows setting OpenSSL security level."""

    def __init__(
        self,
        ssl_context: Optional[ssl.SSLContext] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize the adapter with a custom SSL context.

        Args:
            ssl_context: Optional SSL context to use for HTTPS connections.
            *args: Positional arguments to pass to HTTPAdapter.
            **kwargs: Keyword arguments to pass to HTTPAdapter.
        """
        self.ssl_context = ssl_context
        super().__init__(*args, **kwargs)

    def init_poolmanager(
        self,
        connections: int,
        maxsize: int,
        block: bool = False,
        **pool_kwargs: Any,
    ) -> Any:
        """Initialize the pool manager with custom SSL context."""
        if self.ssl_context:
            pool_kwargs["ssl_context"] = self.ssl_context
        return super().init_poolmanager(  # type: ignore[no-untyped-call]
            connections, maxsize, block, **pool_kwargs
        )


def create_session(openssl_ciphers: Optional[str] = None) -> requests.Session:
    """Create a requests Session with optional OpenSSL cipher configuration.

    Args:
        openssl_ciphers: The OpenSSL cipher string to use for SSL
                        connections. If None or empty, the default SSL
                        configuration is used.
                        Example: "DEFAULT:@SECLEVEL=1"

    Returns:
        A configured requests.Session object.

    Raises:
        ssl.SSLError: If the provided cipher string is invalid.
    """
    session = requests.Session()

    # Only configure custom SSL if cipher string is provided
    if openssl_ciphers and openssl_ciphers.strip():
        # Create a custom SSL context with the specified cipher configuration
        ssl_context = create_urllib3_context()

        # Set the cipher string - this will raise ssl.SSLError if invalid
        try:
            ssl_context.set_ciphers(openssl_ciphers)
        except ssl.SSLError as e:
            raise ssl.SSLError(
                f"Invalid OpenSSL cipher string '{openssl_ciphers}': {e}"
            ) from e

        # Mount the custom adapter for HTTPS
        adapter = SSLAdapter(ssl_context=ssl_context)
        session.mount("https://", adapter)

    return session
