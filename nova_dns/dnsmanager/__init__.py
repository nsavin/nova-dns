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

import re

from nova import flags
from nova.openstack.common import cfg
from nova import log as logging

from abc import ABCMeta, abstractmethod

LOG = logging.getLogger("nova_dns.dnsmanager")
FLAGS = flags.FLAGS

opts = [
    cfg.IntOpt("dns_default_ttl", default=7200,
			help="Default record ttl"),
    cfg.StrOpt("dns_soa_primary", default="ns1",
			help="Name server that will respond authoritatively for the domain"),
    cfg.StrOpt("dns_soa_email", default="hostmaster",
			help="Email address of the person responsible for this zone "),
    cfg.IntOpt("dns_soa_refresh", default=10800,
			help="The time when the slave will try to refresh the zone from the master"),
    cfg.IntOpt("dns_soa_retry", default=3600,
			help="time between retries if the slave fails to contact the master"),
    cfg.IntOpt("dns_soa_expire", default=604800,
			help="Indicates when the zone data is no longer authoritative")
]
FLAGS.register_opts(opts)

record_types=set(('A', 'AAAA', 'MX', 'SOA', 'CNAME', 'PTR', 'SPF', 'SRV', 'TXT', 'NS',
          'AFSDB', 'CERT', 'DNSKEY', 'DS', 'HINFO', 'KEY', 'LOC', 'NAPTR', 'RP', 'RRSIG',
          'SSHFP'))


class DNSManager:
    """abstract class"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def list(self):
        """ should return list of DNSZone objects for all zones"""
        pass

    @abstractmethod
    def add(self, zone_name, soa):
        pass

    @abstractmethod
    def drop(self, zone_name, force=False):
        """ drop zone with all records. return True if was deleted """
        pass

    @abstractmethod
    def get(self, zone_name):
        """ return DNSZone object for zone_name.
        If zone not exist, raise exception
         """
        pass



class DNSZone:
    @abstractmethod
    def __init__(self, zone_name):
        pass
    @abstractmethod
    def drop(self):
        pass
    @abstractmethod
    def add(self, v):
        pass
    @abstractmethod
    def get(self, name, type=None):
        pass
    @abstractmethod
    def set(self, name, type, content, priority, ttl):
        pass
    @abstractmethod
    def delete(self, name, type):
        pass

class DNSRecord:
    def __init__(self, name, type, content, priority=None, ttl=None):
        self.name=DNSRecord.normname(name)
        self.type=DNSRecord.normtype(type)
        self.content=content
        self.priority=int(priority) if priority else 0
        self.ttl=int(ttl) if ttl else FLAGS.dns_default_ttl
    @staticmethod
    def normtype(type):
        t=str(type).upper()
        if t not in record_types:
            raise ValueError("Incorrect type: " + type)
        return t
    @staticmethod
    def normname(n):
        name = str(n).lower()
        if name=="" or name=="*" or re.match(r'\A(?:[\w\d-]+\.)*(?:[\w\d-]+)\Z', name):
            return name
        else:
            raise ValueError("Incorrect DNS name: " + name)

class DNSSOARecord(DNSRecord):
    def __init__(self, primary=None, hostmaster=None, serial=None, refresh=None, retry=None, expire=None, ttl=None):
        self.primary=primary if primary else FLAGS.dns_soa_primary
        self.hostmaster=hostmaster if hostmaster else FLAGS.dns_soa_email
        self.serial=serial if serial else 0
        self.refresh=int(refresh) if refresh else FLAGS.dns_soa_refresh
        self.retry=int(retry) if retry else FLAGS.dns_soa_retry
        self.expire=int(expire) if expire else FLAGS.dns_soa_expire
        DNSRecord.__init__(self, '', 'SOA', '', None, ttl)

