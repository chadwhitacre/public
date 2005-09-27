#!/usr/bin/env python
"""httpy -- a straightforward Python webserver. `man 1 httpy' for details.

The main() function below is inspired by Guido's:

  http://www.artima.com/weblogs/viewpost.jsp?thread=4829

"""

__version__ = (0, 5)
__author__ = 'Chad Whitacre <chad@zetaweb.com>'

import os
import sys

from httpy.Config import ServerConfig
from httpy.Config import ConfigError
from httpy.Server import Server
from httpy.utils import Restart


def _main(argv=None):
    """This is the real main function.
    """

    if argv is None:
        argv = sys.argv[1:]
    try:
        config = ServerConfig(argv)
    except ConfigError, err:
        print >> sys.stderr, err.msg
        print >> sys.stderr, "`man 1 httpy' for usage."
        return 2
    else:
        server = Server(config)
        server.start()


def main(args=None):
    """This is a wrapper around _main to support restarting dynamically.
    """

    if "HTTPY_RESTART_FLAG" in os.environ:
        return _main()
    else:
        while 1:
            try:
                if args is None:
                    args = [sys.executable] + sys.argv
                if sys.platform == "win32":
                    args = ['"%s"' % arg for arg in args]
                new_environ = os.environ.copy()
                new_environ["HTTPY_RESTART_FLAG"] = '/me waves'
                exit_code = os.spawnve(os.P_WAIT, sys.executable,
                                       args, new_environ)
                if exit_code != 3:
                    return exit_code
            except KeyboardInterrupt:
                break
            except:
                raise


if __name__ == "__main__":
    sys.exit(main())



