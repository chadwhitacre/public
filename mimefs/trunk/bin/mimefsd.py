#!/usr/bin/env python
"""mimefsd -- a MIME filesystem XMLRPC server.
"""
import logging
import os
import sys

import mimefslib
from httpy.Config import ConfigError
from httpy.Config import Config
from httpy.Server import Server
from httpy.Server import RestartingServer
from httpy.apps.XMLRPC import XMLRPCApp


format = "%(name)-16s %(levelname)-8s %(message)s"
logging.basicConfig( level=logging.DEBUG
                   , format=format
                    )
logger = logging.getLogger('mimefsd')


# Define some httpy usables.
# ==========================
# We have to jump through hoops since we aren't on the local filesystem.

from httpy.Task import Task
def _validate(self):
    pass
Task.validate = _validate # hoop

class Application(XMLRPCApp, mimefslib.Server):
    uri_root = '/' # hoop


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
        print >> sys.stderr, "`man 1 mimefsd' for usage."
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
