#!/usr/bin/env python
"""
"""

__version__ = (0, 1)
__author__ = 'Chad Whitacre <chad@zetaweb.com>'

import sys

from zetaserver.Server import XMLRPCServer


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    Server._listen = True
    server = XMLRPCServer()
    server.start()


if __name__ == "__main__":
    sys.exit(main())
