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
from cement.core.foundation import CementApp
from cement.core.controller import CementBaseController
from cement.core.controller import expose
from cepces.xcep import Service as XCEPService
from cepces.wstep import Service as WSTEPService
from configparser import NoOptionError
from requests import ConnectionError
from requests import RequestException
import os
import textwrap
import traceback

EISSUED = 0
EWAIT = 1
EREJECTED = 2
ECONNECTERROR = 3
EUNDERCONFIGURED = 4
EWAITMORE = 5
EUNSUPPORTED = 6


class AbstractBaseController(CementBaseController):
    class Meta:
        arguments = [
            (['-e', '--endpoint'], dict(help='endpoint URI')),
            (['-a', '--authentication'],
             dict(choices=['none', 'kerberos'],
                  help='authentication method')),
            ]


class BaseController(AbstractBaseController):
    class Meta:
        label = 'base'
        description = '\n'.join(textwrap.wrap(
            'This utility interacts with a Certificate Enrollment Policy '
            '(CEP) or Certificate Enrollment (CES) service.'
        ))


class SubmissionController(AbstractBaseController):
    '''This controller is used for integration with `certmonger`.

    It should not be called directly.'''
    class Meta:
        hide = True
        label = 'submit'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = '\n'.join(textwrap.wrap(
            'This controller is used for integration with `certmonger` '
            'and should not be called directly.'
        ))

    @expose(hide='True', help='Process a certmonger call.')
    def submit(self):
        # Configuration file sanity check.
        if not self.app.config.has_section('global'):
            self.app.log.error('No global section found in configuration.')
            return EUNDERCONFIGURED

        # Try to get the CES service endpoint from the CEP service.
        try:
            endpoint = self.app.config.get('global', 'endpoint')
            self.app.log.debug('Endpoint is: {0:s}'.format(endpoint))
        except NoOptionError:
            self.app.log.error('No "endpoint" configured.')
            return EUNDERCONFIGURED

        try:
            authentication = self.app.config.get('global', 'authentication')
            self.app.log.debug(
                'Authentication is: {0:s}'.format(authentication)
            )
        except NoOptionError:
            self.app.log.error('No "authentication" configured.')
            return EUNDERCONFIGURED

        try:
            cas = self.app.config.get('global', 'cas')
            self.app.log.debug('CA path is: {0:s}'.format(cas))
        except NoOptionError:
            self.app.log.error('No "cas" configured.')
            return EUNDERCONFIGURED

        if cas == "False":
            cas = False

        cep = XCEPService(
            endpoint=endpoint,
            auth=authentication,
            capath=cas,
        )

        # Get the template name.
        self.app.log.debug('Reading CERTMONGER_CA_PROFILE from environment.')

        if 'CERTMONGER_CA_PROFILE' not in os.environ:
            self.app.log.error('No certmonger CA profile defined.')
            return EUNDERCONFIGURED

        try:
            uris = cep.resolve(os.environ['CERTMONGER_CA_PROFILE'],
                               authentication)
        except (ConnectionError, RequestException, LookupError):
            traceback.print_exc()
            return EREJECTED

        if not uris:
            self.app.log.error('No CEP URIs found.')
            return EREJECTED

        # Get the first URI.
        uri = uris[0]
        self.app.log.debug('Using first URI: {0:s}'.format(uri))

        ces = WSTEPService(
            endpoint=uri,
            auth=authentication,
            capath=cas,
        )

        self.app.log.debug('Reading CERTMONGER_CSR from environment.')
        csr = os.environ['CERTMONGER_CSR']

        try:
            certs = ces.request(csr)
        except ConnectionError:
            self.app.log.error('Connection error:')
            traceback.print_exc()
            return ECONNECTERROR
        except RequestException:
            traceback.print_exc()
            return ECONNECTERROR

        if not certs:
            self.app.log.error('No certificates received.')
            return EREJECTED
        else:
            print('-----BEGIN CERTIFICATE-----')
            print((certs[0].token.text))
            print('-----END CERTIFICATE-----')

    @expose(hide='True', help='Process a certmonger call.')
    def default(self):
        # Dict of available operations.
        operations = {
            'SUBMIT': self.submit,
        }

        # Get the operation, if any, from the environment.
        self.app.log.debug('Reading CERTMONGER_OPERATION from environment.')

        if 'CERTMONGER_OPERATION' not in os.environ:
            self.app.log.error('No certmonger operation defined.')
            self.app.close(EUNDERCONFIGURED)
        # Make sure the operation is implemented.
        elif os.environ['CERTMONGER_OPERATION'] not in operations:
            self.app.log.error('Operation ({0:s}) not implemented.'.format(
                os.environ['CERTMONGER_OPERATION']
            ))
            self.app.close(EUNSUPPORTED)
        else:
            # Call the requested operation.
            operation = operations[os.environ['CERTMONGER_OPERATION']]
            self.app.log.debug('Calling {0:s}()'.format(str(operation)))
            self.app.close(operation())


class Application(CementApp):
    class Meta:
        label = 'cepces'
        handlers = [BaseController,
                    SubmissionController]

        # Set sane configuration file default locations. This should be enough
        # to support most Linux distributions, as well as FreeBSD. Even though
        # FreeBSD is not yet supported (due to the lack of certmonger).
        config_files = [
            '/etc/cepces/cepces.conf',
            '/usr/local/etc/cepces/cepces.conf',
            './conf/cepces.conf',
        ]
