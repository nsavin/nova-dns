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

__version__ = "0.3.0"

try:
    from nova import flags
    from nova.openstack.common import cfg

    FLAGS = flags.FLAGS

    opts = [
	cfg.StrOpt("dns_manager", default="nova_dns.dnsmanager.powerdns.Manager",
			    help="DNS manager class"),
	cfg.StrOpt("dns_listener", default="nova_dns.listener.simple.Listener",
			    help="Class to process AMQP messages"),
	cfg.StrOpt("dns_api_paste_config", default="/etc/nova-dns/dns-api-paste.ini",
			    help="File name for the paste.deploy config for nova-dns api")
    ]
    FLAGS.register_opts(opts)
    
except:
    #make setup.py happy
    pass

