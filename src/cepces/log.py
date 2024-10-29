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
"""This module contains logging configuration."""
from pathlib import Path
import logging.config
from cepces import __title__

# Load logging configuration settings properly.
LOGGING_CONFIG_FILES = [
    "{}/logging.conf".format(__title__),
    "/etc/{}/logging.conf".format(__title__),
    "/usr/local/etc/{}/logging.conf".format(__title__),
]


def init_logging():
    """Initialize logging by reading all (possible) configuration files."""
    for path in [Path(x) for x in LOGGING_CONFIG_FILES]:
        if path.is_file():
            logging.config.fileConfig(path.__str__())
