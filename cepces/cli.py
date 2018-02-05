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
from cepces import Base, DEFAULT_CONFIG_FILES, DEFAULT_CONFIG_DIRS
from cepces.command import Command
from cepces.core import Configuration, Service
from configparser import ConfigParser, ExtendedInterpolation
from pathlib import Path
import argparse
import logging
import socket


class ApplicationError(RuntimeError):
    def __init__(self, message, code):
        super().__init__(message)
        self.code = code


class Application(Base):
    APP_NAME = 'cepces'

    def __init__(self, args=None, logger=None):
        super().__init__(logger=logger)

        self._logger.debug('Initializing application.')

        # Set defaults and store arguments.
        self._exit_code = 0
        self._args = args
        self._config_files = DEFAULT_CONFIG_FILES
        self._config_dirs = DEFAULT_CONFIG_DIRS

        # First initialize the configuration files. Then, let the parser
        # work and override any settings.
        self._init_conf()
        self._init_parser()
        self._init_subparsers()

        args = self._parser.parse_args(args=self._args)
        self._parsed_args = args

        if hasattr(args, 'func') and hasattr(args.func, '__call__'):
            self._action = args.func
        else:
            self._parser.print_help()
            raise ApplicationError('No command specified', 1)

    def _init_conf(self):
        self._logger.debug('Initializing application configuration.')
        self._config = ConfigParser(interpolation=ExtendedInterpolation())
        self._config.optionxform = str  # Make options case sensitive.

        # Add some defaults.
        hostname = socket.gethostname().lower()
        fqdn = socket.getfqdn()
        shortname = hostname.split('.')[0]

        self._config['DEFAULT']['hostname'] = hostname.lower()
        self._config['DEFAULT']['HOSTNAME'] = hostname.upper()
        self._config['DEFAULT']['fqdn'] = fqdn.lower()
        self._config['DEFAULT']['FQDN'] = fqdn.upper()
        self._config['DEFAULT']['shortname'] = shortname.lower()
        self._config['DEFAULT']['SHORTNAME'] = shortname.upper()

        # Read all configuration files.
        for path in [Path(x) for x in self._config_files]:
            if path.is_file():
                self._logger.debug('Reading: {0:s}'.format(path.__str__()))
                self._config.read(path.__str__())

        # Read all configuration directories.
        for cdir in [Path(x) for x in self._config_dirs]:
            if cdir.is_dir():
                for path in sorted([x for x in cdir.iterdir() if x.is_file()]):
                    self._logger.debug('Reading: {0:s}'.format(path.__str__()))
                    self._config.read(path)

    def _init_parser(self):
        parser = argparse.ArgumentParser(Application.APP_NAME)
        self._parser = parser

        verbosity = parser.add_mutually_exclusive_group(required=False)
        verbosity.add_argument(
            '-v',
            '--verbose',
            action='store_true',
            help='increase output',
        )
        verbosity.add_argument(
            '-d',
            '--debug',
            action='store_true',
            help='turn on debugging',
        )

        parser.add_argument(
            '-e',
            '--endpoint',
            help='specify CEP/XCEP endpoint',
        )
        parser.add_argument(
            '-a',
            '--auth',
            help='specify authentication method',
            choices=[
                'Anonymous',
                'Kerberos',
                'UsernamePassword',
                'Certificate',
            ],
        )
        parser.add_argument(
            '-c',
            '--cas',
            help='path to CA certificates',
        )

        # Kerberos settings
        parser.add_argument(
            '-k',
            '--keytab',
            help='Kerberos keytab',
        )
        parser.add_argument(
            '-r',
            '--realm',
            help='Kerberos realm',
        )
        parser.add_argument(
            '-i',
            '--init-ccache',
            help='initialize Kerberos credential cache',
        )
        parser.add_argument(
            '-n',
            '--principals',
            help='comma separated list of Kerberos principals to try',
        )
        parser.add_argument(
            '-t',
            '--enctypes',
            help='comma separated list of Kerberos encryption types to use',
        )

        # Username and Password specific settings
        parser.add_argument(
            '-u',
            '--username',
            help='username for authentication',
        )
        parser.add_argument(
            '-p',
            '--password',
            help='password for authentication',
        )

        # Certificate settings
        # TODO

    def _init_subparsers(self):
        # Find all sub command classes, instantiate them, and allow them to
        # self-register.
        subparsers = self._parser.add_subparsers(help='sub-command help')

        for subclass in Command.__subclasses__():
            instance = subclass(self)
            instance.register(subparsers)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def _parse_args(self):
        config = self._config
        args = self._parsed_args

        # Parse all (possible) arguments.
        if args.verbose:
            logging.getLogger().setLevel(logging.INFO)
        elif args.debug:
            logging.getLogger().setLevel(logging.DEBUG)

        if args.endpoint:
            config['global']['endpoint'] = args.endpoint

        if args.auth:
            config['global']['auth'] = args.auth

        if args.cas:
            if args.cas == '':
                config['global']['cas'] = args.cas
            else:
                config['global']['cas'] = False

        # Kerberos settings
        if args.keytab:
            config['kerberos']['keytab'] = args.keytab

        if args.realm:
            config['kerberos']['realm'] = args.realm

        if args.init_ccache:
            config['kerberos']['ccache'] = args.init_ccache

        if args.principals:
            config['kerberos']['principals'] = args.principals

        if args.enctypes:
            config['kerberos']['enctypes'] = args.enctypes

        # Username and Password  settings
        if args.username:
            config['usernamepassword']['username'] = args.username

        if args.password:
            config['usernamepassword']['password'] = args.password

        # Certificate settings
        # TODO

    def run(self):
        # Parse all arguments, then run the desired action.
        self._parse_args()
        config = Configuration.from_parser(self.config)
        self._service = Service(config)
        self._action()

    @property
    def exit_code(self):
        return self._exit_code

    @exit_code.setter
    def exit_code(self, value):
        self._exit_code = value

    @property
    def config(self):
        return self._config

    @property
    def service(self):
        return self._service
