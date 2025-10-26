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
import unittest
from cryptography import x509
from configparser import ConfigParser
from cepces.config import Configuration
from cepces.core import Service
from cepces.user import UserEnrollment, ApprovalPendingException, load_config


class TestUser(unittest.TestCase):
    """Tests the User cert workflows"""
    """needs a reachable CEP/CES server and valid kerberos credential cache"""

    """make sure your test server has the following cert templates available"""
    test_template_name_auto_approve   = "User"
    test_template_name_manual_approve = "UserManualApprove"

    def _init(self):
        g_overrides = {}
        k_overrides = {
            "ccache": "False",
            "principals": "",
        }
        return UserEnrollment(g_overrides, k_overrides)

    def _check_cert(self, cert_file):
        with open(cert_file, "rb") as f:
            cert = x509.load_pem_x509_certificate(f.read())

    def testRequest(self):
        user_enrollment = self._init()

        self.assertIsInstance(user_enrollment.service, Service)
        self.assertIsInstance(user_enrollment.service._config, Configuration)
        self.assertIsInstance(user_enrollment.service._config.parser, ConfigParser)

        # test loading config
        key_file, cert_file, req_file, profile, renew_days, key_size = load_config(user_enrollment.service._config.parser)

        # test cert template list
        template_list = user_enrollment.service.templates
        self.assertIn(self.test_template_name_auto_approve, template_list)
        self.assertIn(self.test_template_name_manual_approve, template_list)

        # test auto approved cert
        user_enrollment.request(key_file, cert_file, self.test_template_name_auto_approve, key_size, None)
        self._check_cert(cert_file)

        # test manual approved cert
        with self.assertRaises(ApprovalPendingException):
            user_enrollment.request(key_file, cert_file, self.test_template_name_manual_approve, key_size, None)
