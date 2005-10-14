#!/usr/bin/env python
"""Listen for a TCP request and echo it to both stdout and stderr.

Writing it to both streams makes it easy to both capture and watch it.
"""

import sys
from SocketServer import TCPServer
from SocketServer import StreamRequestHandler


class Server(TCPServer):
    allow_reuse_address = True


class Handler(StreamRequestHandler):

    def handle(self):
        for line in self.rfile:
            print >> sys.stdout, line; sys.stdout.flush()
            print >> sys.stderr, line; sys.stderr.flush()



addr = ('', 5370)
server = Server(addr, Handler)
server.handle_request()
