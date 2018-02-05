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
from abc import ABCMeta, abstractmethod
from cepces import Base
from cepces.certmonger.core import MissingEnvironmentVariable
from cepces.certmonger.core import Result as CertmongerResult
from cepces.certmonger.operation import Operation as CertmongerOperation
import os


class Command(Base, metaclass=ABCMeta):
    def __init__(self, application):
        super().__init__()

        self._application = application

    @abstractmethod
    def __call__(self):
        pass

    @abstractmethod
    def register(self, subparsers):
        pass


class Certmonger(Command):
    """Submission handler for certmonger."""
    def __init__(self, application):
        super().__init__(application)

        self._operations = {}

    def __call__(self):
        if 'CERTMONGER_OPERATION' not in os.environ:
            raise MissingEnvironmentVariable('CERTMONGER_OPERATION')

        operation = os.environ['CERTMONGER_OPERATION']

        # Find all supported certmonger operations.
        for subclass in CertmongerOperation.__subclasses__():
            self._operations[subclass._name_] = subclass

        # If the operation is available, call it. Otherwise, return an error
        # code.
        if operation not in self._operations.keys():
            return CertmongerResult.UNSUPPORTED
        else:
            operation = self._operations[operation](self._application)

            return operation()

    def register(self, subparsers):
        self._parser = subparsers.add_parser(
            'certmonger',
            help='Submission handler for certmonger',
        )
        self._parser.set_defaults(func=self)


class Templates(Command):
    def __init__(self, application):
        super().__init__(application)

    def __call__(self):
        """Queries the XCEP service for all available templates."""
        print('The following templates are available:\n')
        for template in self._application.service.templates:
            print(template)

    def register(self, subparsers):
        self._parser = subparsers.add_parser(
            'templates',
            help='List all available templates',
        )
        self._parser.set_defaults(func=self)
