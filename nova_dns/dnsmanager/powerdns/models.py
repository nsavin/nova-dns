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
SQLAlchemy models for Nova PowerDNS.
"""

from sqlalchemy.orm import object_mapper
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Index 

from nova_dns.dnsmanager.powerdns.session import get_session, get_engine


BASE = declarative_base()


class PowerDNSBase(object):
    """Base class for Nova DNS Models."""
    _i = None

    def save(self, session=None):
        """Save this object."""

        if not session:
            session = get_session()
        session.add(self)
        try:
            session.flush()
        except IntegrityError:
            raise

    def delete(self, session=None):
        """Delete this object."""
        self.save(session=session)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def get(self, key, default=None):
        return getattr(self, key, default)

    def __iter__(self):
        self._i = iter(object_mapper(self).columns)
        return self

    def next(self):
        n = self._i.next().name
        return n, getattr(self, n)

    def update(self, values):
        """Make the model object behave like a dict"""
        for k, v in values.iteritems():
            setattr(self, k, v)

    def iteritems(self):
        """Make the model object behave like a dict.

        Includes attributes from joins."""
        local = dict(self)
        joined = dict([(k, v) for k, v in self.__dict__.iteritems()
                      if not k[0] == '_'])
        local.update(joined)
        return local.iteritems()


class Domains(BASE, PowerDNSBase):
    __tablename__ = 'domains'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    #TODO now only 'NATIVE' sync supported (with database
    #replication/copying outside of powerdns). Add support via AXFR.
    #Change fields to NOT NULL.
    master = Column(String(255), nullable=True)
    last_check = Column(Integer, nullable=True)
    type = Column(String(6), nullable=True)
    notified_serial = Column(Integer, nullable=True)
    account = Column(String(40), nullable=True)

class Records(BASE, PowerDNSBase):
    __tablename__ = 'records'
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_id = Column(Integer, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(6), nullable=False)
    content = Column(String(255))
    ttl = Column(Integer)
    prio = Column(Integer)
    change_date = Column(Integer)

Index('nametype_index', Records.name, Records.type, unique=True)

def register_models():
    """Register Models and create metadata."""
    models = (Domains, Records)
    engine = get_engine()
    for model in models:
        model.metadata.create_all(engine)
    

