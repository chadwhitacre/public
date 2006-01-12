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

    def _connect(self, name):
        """Given a database name, return a database connection.
        """
        try:
            return psycopg.connect('dbname=%s' % name)
        except:
            raise StandardError("Bad db name: '%s'" % name)

    def _verify(self, key):
        """Given the master key, verify that it is correct.
        """
        if key != KEY:
            raise StandardError("Bad key: '%s'" % key)


    # Cluster management
    # ==================

    def create(self, key):
        """Given the master key, return the name of the new database.
        """
        self._verify(key)

        # Generate a database name.
        # =========================
        # Currently we depend on uuid(1) in the OS.

        p = subprocess.Popen(('uuid','-v4'), stdout=subprocess.PIPE)
        name = p.stdout.read().replace('-','')


        # Create the database and return its name.
        # ========================================

        p = subprocess.Popen( ( 'createdb'
                              , '--template'
                              , 'template_mimedb_0'
                              , name
                               )
                            , stdout=subprocess.PIPE
                             )
        result = p.stdout.read()
        if result != 'CREATE DATABASE\n':
            raise StandardError("Failed to create database: '%s'" % result)
        return name

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

    def drop(self, key):
        """Takes the master key and a database name.
        """
        self._verify(key)
        raise NotImplementedError


    # Message API
    # ===========

    def all(self, key):
        """Return a list of all message IDs.
        """
        raise NotImplementedError


    def find(self, key, criteria):
        """Given criteria, returning message IDs of matching messages.
        """
        raise NotImplementedError


    def headers(self, key, msg_id):
        """Given a message ID, retrieve the message's headers.
        """
        raise NotImplementedError


    def remove(self, key, msg_id):
        """Given a message ID, remove the message.
        """
        raise NotImplementedError


    def replace(self, key, msg_id, msg):
        """Replace one message with another.

        This does a store and a remove within one transaction, and is
        effectively an update operation. The wrinkle is that to us, the contents
        of the file determine its uniqueness, but any given application will
        undoubtedly impute identity to messages that according to our definition
        are not identical. Since any such imputation is application dependant,
        we don't support it beyond this convenience method.

        """
        raise NotImplementedError


    def retrieve(self, key, msg_id):
        """Given a message ID, return a MIME message.
        """
        raise NotImplementedError


    def single(self, key, msg_id):
        """Just like find, but raise an error if there is more than one match.
        """
        raise NotImplementedError


    def store(self, key, msg):
        """Given a MIME message, store it.
        """
        conn = self._connect(key)
        # need to quote/escape msg
        SQL = "INSERT INTO data (datum) VALUES (%s)" % msg
        conn.execute(SQL)

        # self.write('2 Already stored.') -
        # does this bring us back to msg_id as hash?

        # Make sure we stored it successfully.
        # ====================================

        disk = open(path, 'rb').read()
        disk_id = sha.new(disk).hexdigest()
        if disk_id != msg_id:
            self.write('2 Message storage failed! (server)')


        # Index and return.
        # =================

        for header, value in message_from_string(msg).items():
            db_path = os.path.join(self.metadata_root, header.lower())
            db = anydbm.open(db_path, 'c')
            db[msg_id] = value
            db.close()

        self.write('0 %s' % disk_id)


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
