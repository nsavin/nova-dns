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

from nova import log as logging
from nova import flags

from abc import ABCMeta, abstractmethod

LOG = logging.getLogger("nova_dns.listener")
FLAGS = flags.FLAGS



class AMQPListener:
    """abstract class"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def event(self, event):
        """process event"""
        pass
