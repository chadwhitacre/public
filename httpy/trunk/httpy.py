#!/usr/bin/env python
"""httpy -- a straightforward Python webserver. `man 1 httpy' for details.

The main() function below is inspired by Guido:

  http://www.artima.com/weblogs/viewpost.jsp?thread=4829

"""

__version__ = (0,1)
__author__ = 'Chad Whitacre <chad@zetaweb.com>'

import sys

from httpy.Server import Server


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    try:
        #config = Configuration(argv)
        config = {}
    except ConfigError, err:
        print >> sys.stderr, err.msg
        print >> sys.stderr, "`man 1 httpy' for usage."
        return 2
    else:
        addr = ('', 8080)
        server = Server(addr)
        server.serve_forever()


if __name__ == "__main__":
    sys.exit(main())
