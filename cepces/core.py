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

from cepces import Base
from cepces.cli import Command
import argparse


class ApplicationError(RuntimeError):
    def __init__(self, message, code):
        super().__init__(message)
        self.code = code


class Application(Base):
    APP_NAME = 'cepces'

    def __init__(self, args=None):
        super().__init__()

        self._args = args
        self._exit_code = 0

        self._init_parser()

    def _init_parser(self):
        self._parser = argparse.ArgumentParser(Application.APP_NAME)

        # Find all sub command classes, instantiate them, and allow them to
        # self-register.
        subparsers = self._parser.add_subparsers(help='sub-command help')

        for subclass in Command.__subclasses__():
            instance = subclass()
            instance.register(subparsers)

        args = self._parser.parse_args(args=self._args)

        if hasattr(args, 'func') and hasattr(args.func, '__call__'):
            args.func()
        else:
            self._parser.print_help()
            raise ApplicationError('No command specified', 1)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def run(self):
        pass

    @property
    def exit_code(self):
        return self._exit_code

    @exit_code.setter
    def exit_code(self, value):
        self._exit_code = value
