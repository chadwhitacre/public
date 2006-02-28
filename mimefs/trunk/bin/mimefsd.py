#!/usr/bin/env python
"""mimefsd -- a MIME filesystem XMLRPC server.
"""
import logging
import os
import sys

import mimefslib
from httpy.couplers import StandAlone
from httpy.responders import XMLRPC


format = "%(name)-16s %(levelname)-8s %(message)s"
logging.basicConfig( level=logging.DEBUG
                   , format=format
                    )
logger = logging.getLogger('mimefsd')


class Responder(XMLRPC, mimefslib.Server):
    """
    """

if __name__ == '__main__':
    import sys
    sys.argv.append('-a:5370')
    responder = Responder()
    coupler = StandAlone(responder)
    coupler.go()
