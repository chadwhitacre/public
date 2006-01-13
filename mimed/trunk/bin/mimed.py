#!/usr/bin/env python
"""mimed -- a MIME database XMLRPC server. `man 1 mimed' for details.
"""

__version__ = (0, 3)
__author__ = 'Chad Whitacre <chad@zetaweb.com>'

import logging
import os
import sha
import signal
import subprocess
import sys
import time
from StringIO import StringIO
from email.Generator import Generator
from email.Message import Message

import psycopg
from httpy.Config import ConfigError
from httpy.Config import Config
from httpy.Server import Server
from httpy.Server import RestartingServer
from httpy.apps.XMLRPC import XMLRPCApp


format = "%(name)-16s %(levelname)-8s %(message)s"
logging.basicConfig( level=logging.DEBUG
                   , format=format
                    )
logger = logging.getLogger('mimed')


# TODO: add check for ownership and permissions
KEY = open('/etc/mimedb.key').read()


# Monkey-patch Task since we don't have anything on the filesystem.
# =================================================================

from httpy.Task import Task
def _validate(self):
    pass
Task.validate = _validate


# Define our Application class.
# =============================

class Application(XMLRPCApp):

    uri_root = '/' # To play nice with httpy until it is more library-friendly.


    # Fundaments
    # ==========

    def echo(self, foo=''):
        return foo

    def _connect(self):
        """Given a database name, return a database connection.
        """
        try:
            return psycopg.connect('dbname=MIMEdb')
        except:
            raise StandardError("Bad db name: '%s'" % name)

    def _verify(self, key):
        """Given the master key, verify that it is correct.
        """
        if key != KEY:
            raise StandardError("Bad key: '%s'" % key)

    def _uuid(self):
        """Return a 32-byte string. Currently we depend on uuid(1) in the OS.
        """
        p = subprocess.Popen(('uuid','-v4'), stdout=subprocess.PIPE)
        return p.stdout.read().replace('-','')


    # Catalogs
    # ========

    def create(self, key):
        """Given the master key, return the cid of a new catalog.
        """
        self._verify(key)
        conn = self._connect()

        cid = self._uuid()
        SQL = "INSERT INTO catalog (cid) VALUES (%s);"
        conn.execute(SQL, (cid,))

        conn.commit()
        conn.close()
        return cid


    def dump(self, key):
        """Given the master key, return a bzip2'd SQL script.
        """
        self._verify(key)
        raise NotImplementedError


    def load(self, key, sql):
        """Takes a bzip2'd SQL script.
        """
        self._verify(key)
        raise NotImplementedError


    def destroy(self, key, cid):
        """Takes the master key and a cid.
        """
        self._verify(key)
        raise NotImplementedError


    # Messages
    # ========

    def all(self, cid):
        """Return a list of all message IDs.
        """
        conn = self._connect()
        conn.close()
        raise NotImplementedError


    def find(self, cid, criteria):
        """Given criteria, returning message IDs of matching messages.
        """
        conn = self._connect(key)
        conn.close()
        raise NotImplementedError


    def headers(self, cid, msg_id):
        """Given a message ID, retrieve the message's headers.
        """
        conn = self._connect(key)
        conn.close()
        raise NotImplementedError


    def remove(self, cid, msg_id):
        """Given a message ID, remove the message.
        """
        conn = self._connect(key)
        conn.close()
        raise NotImplementedError


    def replace(self, cid, msg_id, msg):
        """Replace one message with another.
        """
        conn = self._connect(key)
        conn.close()
        raise NotImplementedError


    def retrieve(self, cid, msg_id):
        """Given a message ID, return a MIME message.
        """
        conn = self._connect(key)
        conn.close()
        raise NotImplementedError


    def single(self, cid, msg_id):
        """Just like find, but raise an error if there is more than one match.
        """
        conn = self._connect(key)
        conn.close()
        raise NotImplementedError


    def store(self, cid, msg):
        """Given a new MIME message, return a mid.
        """
        conn = self._connect(key)


        # Sanitize the message.
        # =====================
        # Flatten a possible Message object, convert all ewlines to \n, and
        # make sure a body-less message has two newlines at the end.

        if isinstance(msg, basestring):
            pass
        elif isinstance(msg, Message):
            fp = StringIO()
            g = Generator(fp, mangle_from_=False, maxheaderlen=60)
            g.flatten(msg)
            msg = fp.getvalue()
        msg = '\n'.join(msg.splitlines())
        if '\n\n' not in msg:
            msg += '\n\n'


        # Store the message.
        # ==================

        mid = self._uuid()
        headers, body = msg.split('\n\n', 1)
        SQL = ( "INSERT INTO message (cid, mid, headers, body) " +
                "VALUES (%s, %s, %s, %s);"
               )
        conn.execute(SQL, (cid, mid, headers, body))


        # Index the message headers.
        # ==========================

        for name, body in message_from_string(headers).items():
            SQL = "INSERT INTO field (mid, name, body) VALUES (%s, %s, %s);"
            conn.execute(SQL, mid, name, body)


        # Wrap up and return.
        # ===================

        conn.commit()
        conn.close()
        return mid



# This is our main callable.
# ==========================

def main(argv=None):

    # Read in configuration options.
    # ==============================
    # We override the default port number

    Config.address = ('', 5370)

    if argv is None:
        argv = sys.argv[1:]
    try:
        config = Config(argv)
    except ConfigError, err:
        print >> sys.stderr, err.msg
        print >> sys.stderr, "`man 1 mimed' for usage."
        return 2


    # Instantiate and start a server.
    # ===============================

    plain_jane = (  (os.environ['HTTPY_MODE'] == 'deployment')
                 or (sys.platform == 'win32')
                 or ('HTTPY_PLAIN_JANE' in os.environ)
                   )
    ServerClass = plain_jane and Server or RestartingServer
    server = ServerClass(config)
    server.apps = [Application()]
    server.start()


if __name__ == "__main__":
    sys.exit(main())
