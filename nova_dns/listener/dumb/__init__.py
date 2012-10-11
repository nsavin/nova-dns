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

"""Dumb listener - only log events """

from nova import log as logging
from nova_dns.listener import AMQPListener

LOG = logging.getLogger("nova_dns.listener.dumb")

methods=set(("run_instance", "terminate_instance", "stop_instance",
    "start_instance", "pause_instance", "unpause_instance",
    "resume_instance", "suspend_instance"))

class Listener(AMQPListener):
    def event(self, e):
        method = e.get("method", "<unknown>")
        if method not in methods:
            LOG.debug("Skip message with method: "+method)
            return
        contextproject_id = e["_context_project_id"]
        id = e["args"]["instance_id"]
        try:
            name = e["args"]["request_spec"]["instance_properties"]["display_name"]
        except:
            name = "<unknown>"
        LOG.warning("Method %s instance_id '%s' project_id '%s' instance name '%s'" %
            (method, str(id), str(contextproject_id), name))
