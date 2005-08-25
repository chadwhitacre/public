#!/usr/bin/env python
"""httpy is an uncomplicated Python webserver. `man 1 httpy' for details.

The main() function below is inspired by Guido:

  http://www.artima.com/weblogs/viewpost.jsp?thread=4829

"""

__version__ = (0,1)
__author__ = 'Chad Whitacre <chad@zetaweb.com>'

import asyncore
import sys

from medusa import http_server

from httpy.Handler import Handler
from httpy.Configuration import ConfigError
from httpy.Configuration import Configuration

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    try:
        config = Configuration(argv)
    except ConfigError, err:
        print >> sys.stderr, err.msg
        print >> sys.stderr, "`man 1 httpy' for usage."
        return 2
    else:
        server = http_server.http_server(**config.server)
        server.install_handler(Handler(**config.handler))
        asyncore.loop()

if __name__ == "__main__":
    sys.exit(main())
