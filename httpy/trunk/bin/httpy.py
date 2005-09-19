#!/usr/bin/env python
"""httpy -- a straightforward Python webserver. `man 1 httpy' for details.

The main() function below is inspired by Guido's:

  http://www.artima.com/weblogs/viewpost.jsp?thread=4829

"""

__version__ = (0, 5)
__author__ = 'Chad Whitacre <chad@zetaweb.com>'

import sys

from httpy.Config import Config
from httpy.Config import ConfigError
from httpy.Server import Server


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    try:
        config = Config(argv).ossify()
    except ConfigError, err:
        print >> sys.stderr, err.msg
        print >> sys.stderr, "`man 1 httpy' for usage."
        return 2
    else:
        server = Server(config)
        server.start()


if __name__ == "__main__":
    sys.exit(main())
