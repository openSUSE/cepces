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
from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='cepces',
    version='0.0.1',

    description='Certificate Enrollment through CEP/CES',
    long_description=long_description,
    url='https://github.com/ufven/cepces',

    author='Daniel Uvehag',
    author_email='daniel.uvehag@gmail.com',

    license='GPLv3+',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Environment :: Console',

        'Intended Audience :: System Administrators',
        'Topic :: System :: Systems Administration',

        'License :: OSI Approved :: '
        'GNU General Public License v3 or later (GPLv3+)',

        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='certificate ca cep ces adcs',

    packages=[
              'cepces',
              'cepces.xml',
    ],

    install_requires=[],

    test_suite='tests'
)
