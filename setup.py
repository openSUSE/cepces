#!/usr/bin/env python3
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
from codecs import open as copen
from os import path
from setuptools import setup
import cepces

HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with copen(path.join(HERE, 'README.rst'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name=cepces.__title__,
    version=cepces.__version__,

    description=cepces.__description__,
    long_description=LONG_DESCRIPTION,
    url=cepces.__url__,

    author=cepces.__author__,
    author_email=cepces.__author_email__,

    license=cepces.__license__,

    classifiers=[
        'Development Status :: 4 - Beta',

        'Environment :: Console',

        'Intended Audience :: System Administrators',
        'Topic :: System :: Systems Administration',

        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='certificate ca cep ces adcs wstep xcep',

    packages=[
        'cepces',
        'cepces.certmonger',
        'cepces.krb5',
        'cepces.soap',
        'cepces.wstep',
        'cepces.xcep',
        'cepces.xml',
    ],

    data_files=[
        ('/usr/local/libexec/certmonger', ['bin/cepces-submit']),
        (
            '/usr/local/etc/cepces',
            [
                'conf/cepces.conf.dist',
                'conf/logging.conf.dist',
            ]
        ),
    ],

    install_requires=[],

    test_suite='tests',
)
