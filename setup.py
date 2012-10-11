#!/usr/bin/env python
#
#    Nova DNS 
#    Copyright (C) GridDynamics Openstack Core Team, GridDynamics
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from setuptools import setup, find_packages
from nova_dns import __version__


setup(name='nova-dns',
      version=__version__,
      license='ASL 2.0',
      description='cloud computing dns toolkit',
      author='Savin Nikita (GridDynamics Openstack Core Team, (c) GridDynamics)',
      author_email='openstack@griddynamics.com',
      url='http://www.griddynamics.com/openstack',
      packages=find_packages(exclude=['bin', 'smoketests', 'tests']),
      scripts=['bin/nova-dns'],
      py_modules=[],
      test_suite='tests'
)

