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

"""Main application package."""

import logging


from pathlib import Path
import logging.config


__title__ = 'cepces'
__description__ = 'CEP/CES library.'
__url__ = 'https://github.com/ufven/cepces/'
__version__ = '0.2.1'
__author__ = 'Daniel Uvehag'
__author_email__ = 'daniel.uvehag@gmail.com'
__license__ = 'GPLv3'
__copyright__ = 'Copyright 2017 Daniel Uvehag'

DEFAULT_CONFIG_FILES = [
    '/etc/cepces/cepces.conf',
    '/usr/local/etc/cepces/cepces.conf',
    'conf/cepces.conf',
    'cepces.conf',
]
DEFAULT_CONFIG_DIRS = [
    '/etc/cepces/conf.d',
    '/usr/local/etc/cepces/conf.d'
    'conf/conf.d',
]

# Load logging configuration settings properly.
LOGGING_CONFIG_FILES = [
    'conf/logging.conf',
    '/etc/cepces/logging.conf',
    '/usr/local/etc/cepces/logging.conf',
]

for path in [Path(x) for x in LOGGING_CONFIG_FILES]:
    if path.is_file():
        logging.config.fileConfig(path.__str__())


class Base(object):
    """Base for most classes.

    This class contains common behaviour for all classes used within the
    project.
    """
    def __init__(self, logger=None):
        """Initialize the instance.

        The class uses either a supplied logger, or retrieves the default
        logger for the instance.

        :param logger: Optional logger.
        """
        name = '{}.{}<0x{:02x}>'.format(
            self.__module__,
            self.__class__.__name__,
            id(self),
        )
        self._logger = logger or logging.getLogger(name)
        self._logger.debug('Initializing {0:s}.'
                           .format(name))

    def __str__(self):
        """Returns a string representation of this instance.

        :return: A string representation of this instance.
        """
        return '{0}<{1}>'.format(self.__class__.__name__, hex(id(self)))
