#!/usr/bin/env python
"""mimed -- a MIME database XMLRPC server. `man 1 mimed' for details.
"""

__version__ = (0, 1)
__author__ = 'Chad Whitacre <chad@zetaweb.com>'

import logging
import os
import signal
import sys
import time

import psycopg
from httpy.Config import ConfigError
from httpy.Config import Config
from httpy.Server import Server
from httpy.Server import RestartingServer
from httpy.apps.XMLRPC import XMLRPCApp


# Define our Application class.
# =============================

class Application(XMLRPCApp):

    uri_root = '/' # To play with httpy.

    def _connect(self, key):
        """Given an API key, return a database connection.
        """
        return psycopg.connect('dbname=%s' % key)


    def all(self, key):
        """Return a list of all message IDs.
        """
        conn = self._connect(key)
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


    def store(self, key, msg):
        """Given a MIME message, store it.
        """
        conn = self._connect(key)
        raise NotImplementedError



def main(argv=None):

    # Read in configuration options.
    # ==============================

    Config.address = ('', 5370)

    if argv is None:
        argv = sys.argv[1:]
    try:
        config = Config(argv)
    except ConfigError, err:
        print >> sys.stderr, err.msg
        print >> sys.stderr, "`man 1 httpy' for usage."
        return 2


    # Set up top-level logging.
    # =========================

    format = "%(name)-16s %(levelname)-8s %(message)s"
    logging.basicConfig( level=logging.DEBUG
                       , format=format
                        )


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
