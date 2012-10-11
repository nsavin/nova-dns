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
"""
Authorization
"""


import ConfigParser

from nova import flags
from nova.openstack.common import cfg
from keystoneclient.v2_0 import client as keystone_client
from dnsmanager import DNSRecord

FLAGS = flags.FLAGS

opts = [
    cfg.StrOpt("dns_auth", default="keystone", help="Auth mode in REST API"),
    cfg.StrOpt("dns_auth_role", default="DNS_Admin", help="Role name in REST API"),
    cfg.StrOpt("dns_nova_auth", default="keystone", help="Auth mode in Nova"),
    cfg.StrOpt("dns_zone", default="localzone", help="Nova DNS base zone")
]
FLAGS.register_opts(opts)



class NoAuth(object):
    def tenant2zonename(self, project_id):
        return "%s.%s" % (DNSRecord.normname(project_id), FLAGS.dns_zone)
    def can(self, req, zone_name): 
        return {"read":True, "write":True}

class KeystoneAuth(NoAuth):
    def __init__(self):
        config = ConfigParser.RawConfigParser()
        config.read(FLAGS.dns_api_paste_config)
        self.token = config.get("filter:authtoken", "admin_token")
        self.url = "%s://%s:%s/v2.0" % (
            config.get("filter:authtoken", "auth_protocol"),
            config.get("filter:authtoken", "auth_host"),
            config.get("filter:authtoken", "auth_port"))
        self.client = keystone_client.Client(
            endpoint=self.url, token=self.token)
        self.tenants = {}

    def tenant2zonename(self, project_id):
        #project_id is a really project_id :)
        return super(KeystoneAuth, self).tenant2zonename(self._get_tenant(project_id))
    
    def can(self, req, zone_name): 
        roles = [r.strip()
                 for r in req.headers.get('X_ROLE', '').split(',')]
        if "Admin" in roles:
            return {"read":True, "write":True}
        if FLAGS.dns_auth_role not in roles:
            return {"read":True, "write":False}
        # will raise if no X_TENANT_ID header
        name = self.tenant2zonename(req.headers['X_TENANT_ID'])
        can_write = DNSRecord.normname(zone_name) == DNSRecord.normname(name)
        return {"read":True, "write":can_write}


    def _get_tenant(self, id):
        if not self.tenants.has_key(id):
            #probably new tenant, let's re-read cache
            self.tenants={}
            for t in self.client.tenants.list():
                self.tenants[t.id] = t.name
        name = self.tenants.get(id, None)
        if not name:
            #nope, not new
            raise ValueError('Unknown tenant_id: %s' % (str(id)))
        return name

AUTH = NoAuth() if FLAGS.dns_auth == 'none' else KeystoneAuth()

