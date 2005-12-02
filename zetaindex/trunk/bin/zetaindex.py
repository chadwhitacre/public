#!/usr/bin/env python
"""
"""

__version__ = (0, 1)
__author__ = 'Chad Whitacre <chad@zetaweb.com>'

import sys

from zetaserver.Index import Index
from zetaserver.Server import XMLRPCServer


def foo():
    return 'bar'


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    server = XMLRPCServer()
    server.register_instance(Index)
    server.start()


if __name__ == "__main__":
    sys.exit(main())
