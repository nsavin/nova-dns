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

"""Session Handling for SQLAlchemy backend."""

import sqlalchemy.exc
import sqlalchemy.orm
import time

import nova.exception
from nova import flags
from nova.openstack.common import cfg
from nova import log as logging


FLAGS = flags.FLAGS

opts = [
    cfg.StrOpt('dns_sql_connection',
                default="mysql://pdns:pdns@localhost/pdns",
#              'sqlite:////var/lib/nova/nova_dns.sqlite',
                help='connection string for powerdns sql database')
]
FLAGS.register_opts(opts)


LOG = logging.getLogger("nova_dns.dnsmanager.powerdns.session")

_ENGINE = None
_MAKER = None


def get_session(autocommit=True, expire_on_commit=False):
    """Return a SQLAlchemy session."""
    global _ENGINE, _MAKER

    if _MAKER is None or _ENGINE is None:
        _ENGINE = get_engine()
        _MAKER = get_maker(_ENGINE, autocommit, expire_on_commit)

    session = _MAKER()
    session.query = nova.exception.wrap_db_error(session.query)
    session.flush = nova.exception.wrap_db_error(session.flush)
    return session


def get_engine():
    """Return a SQLAlchemy engine."""
    connection_dict = sqlalchemy.engine.url.make_url(FLAGS.dns_sql_connection)

    engine_args = {
        "pool_recycle": FLAGS.sql_idle_timeout,
        "echo": False,
    }

    if "sqlite" in connection_dict.drivername:
        engine_args["poolclass"] = sqlalchemy.pool.NullPool

    engine = sqlalchemy.create_engine(FLAGS.dns_sql_connection, **engine_args)
    ensure_connection(engine)
    return engine


def ensure_connection(engine):
    remaining_attempts = FLAGS.sql_max_retries
    while True:
        try:
            engine.connect()
            return
        except sqlalchemy.exc.OperationalError:
            if remaining_attempts == 0:
                raise
            LOG.warning(_('SQL connection failed (%(connstring)s). '
                          '%(attempts)d attempts left.'),
                           {'connstring': FLAGS.dns_sql_connection,
                            'attempts': remaining_attempts})
            time.sleep(FLAGS.sql_retry_interval)
            remaining_attempts -= 1


def get_maker(engine, autocommit=True, expire_on_commit=False):
    """Return a SQLAlchemy sessionmaker using the given engine."""
    return sqlalchemy.orm.sessionmaker(bind=engine,
                                       autocommit=autocommit,
                                       expire_on_commit=expire_on_commit)
