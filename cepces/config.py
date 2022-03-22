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
import socket
from cepces import Base
from cepces import auth as CoreAuth
from cepces.soap import auth as SOAPAuth


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


class Configuration(Base):
    """Base configuration class."""
    AUTH_HANDLER_MAP = {
        'Anonymous': CoreAuth.AnonymousAuthenticationHandler,
        'Kerberos': CoreAuth.KerberosAuthenticationHandler,
        'UsernamePassword': CoreAuth.UsernamePasswordAuthenticationHandler,
        'Certificate': CoreAuth.CertificateAuthenticationHandler,
    }

    AUTH_MAP = {
        'Anonymous': SOAPAuth.AnonymousAuthentication,
        'Kerberos': SOAPAuth.TransportKerberosAuthentication,
        'UsernamePassword': SOAPAuth.MessageUsernamePasswordAuthentication,
        'Certificate': SOAPAuth.TransportCertificateAuthentication,
    }

    def __init__(self, endpoint, endpoint_type, cas, auth, poll_interval):
        super().__init__()

        self._endpoint = endpoint
        self._endpoint_type = endpoint_type
        self._cas = cas
        self._auth = auth
        self.pollInterval = poll_interval

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

    @classmethod
    def load(cls, files=None, dirs=None, global_overrides=None,
             krb5_overrides=None):
        """Load configuration files and directories and instantiate a new
        Configuration."""
        name = '{}.{}'.format(
            cls.__module__,
            cls.__name__,
        )
        logger = logging.getLogger(name)

        logger.debug('Initializing application configuration.')
        config = ConfigParser(interpolation=ExtendedInterpolation())
        config.optionxform = str  # Make options case sensitive.

        # Add some defaults.
        hostname = socket.gethostname().lower()
        fqdn = socket.getfqdn()
        shortname = hostname.split('.')[0]

        config['DEFAULT']['hostname'] = hostname.lower()
        config['DEFAULT']['HOSTNAME'] = hostname.upper()
        config['DEFAULT']['fqdn'] = fqdn.lower()
        config['DEFAULT']['FQDN'] = fqdn.upper()
        config['DEFAULT']['shortname'] = shortname.lower()
        config['DEFAULT']['SHORTNAME'] = shortname.upper()

        if files is None:
            files = DEFAULT_CONFIG_FILES

        if dirs is None:
            dirs = DEFAULT_CONFIG_DIRS

        # Read all configuration files.
        for path in [Path(x) for x in files]:
            if path.is_file():
                logger.debug('Reading: {0:s}'.format(path.__str__()))
                config.read(path.__str__())

        # Read all configuration directories.
        for cdir in [Path(x) for x in dirs]:
            if cdir.is_dir():
                for path in sorted([x for x in cdir.iterdir() if x.is_file()]):
                    logger.debug('Reading: {0:s}'.format(path.__str__()))
                    config.read(path)

        # Override globals set from the command line
        if global_overrides is not None:
            for key, val in global_overrides.items():
                config['global'][key] = val
        if krb5_overrides is not None:
            for key, val in krb5_overrides.items():
                config['kerberos'][key] = val

        return Configuration.from_parser(config)

    @classmethod
    def from_parser(cls, parser):
        """Create a Configuration instance from a ConfigParser."""
        # Ensure there's a global section present.
        if 'global' not in parser:
            raise RuntimeError('Missing "global" section in configuration.')

        section = parser['global']

        # Ensure certain required variables are present.
        for var in ['endpoint', 'auth', 'type', 'poll_interval']:
            if var not in section:
                raise RuntimeError(
                    'Missing "{}/{}" variable in configuration.'.format(
                        'global',
                        var,
                    ),
                )

        # Verify that the chosen authentication method is valid.
        if section['auth'] not in Configuration.AUTH_HANDLER_MAP.keys():
            raise RuntimeError(
                'No such authentication method: {}'.format(
                    section['auth'],
                ),
            )

        # Store the global configuration options.
        endpoint = section.get('endpoint')
        endpoint_type = section.get('type')
        authn = Configuration.AUTH_HANDLER_MAP[section['auth']](parser)
        cas = section.get('cas', True)
        poll_interval = section.get('poll_interval')

        if cas == '':
            cas = False

        return Configuration(endpoint, endpoint_type, cas, authn.handle(), poll_interval)
