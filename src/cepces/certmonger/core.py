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

"""This module contains common shared certmonger classes."""

from enum import IntEnum


class Result(IntEnum):
    """This enumeration contains the result codes expected by certmonger."""

    DEFAULT = 0
    ISSUED = 0
    WAIT = 1
    REJECTED = 2
    CONNECTERROR = 3
    UNDERCONFIGURED = 4
    WAITMORE = 5
    UNSUPPORTED = 6


class MissingEnvironmentVariable(RuntimeError):
    """This error is raised when an expected environment variable is
    missing."""

    def __init__(self, variable: str) -> None:
        """Initializes the error.

        :param variable: the name of the missing environment variable.
        """
        self._variable = variable

        super().__init__(
            "The mandatory environment variable {} is missing, "
            "cannot proceed.".format(variable)
        )

    @property
    def variable(self):
        """Returns the name of the missing environment variable.

        :return: the name of the missing environment variable.
        """
        return self._variable
