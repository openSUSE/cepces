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

"""Module containing common classes and functionality."""

import logging


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
        self._logger = logger or logging.getLogger(repr(self))
        self._logger.debug('Initializing {0:s}.'
                           .format(self.__class__.__name__))

    def __str__(self):
        """Returns a string representation of this instance.

        :return: A string representation of this instance.
        """
        return '{0}<{1}>'.format(self.__class__.__name__, hex(id(self)))
