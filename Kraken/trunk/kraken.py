#!/usr/bin/env python

import os
import sys

from kraken.Kraken import Kraken


class Usage(Exception):
    def __init__(self, msg=''):
        self.msg = msg
        Exception.__init__()


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    try:
        if len(argv) == 0:
            path = '.'
        elif len(argv) == 1:
            path = argv[0]
        else:
            raise Usage("too many arguments")
        path = os.path.realpath(path)
        if not os.path.isdir(path):
            raise Usage("%s does not point to a directory." % path)

    except Usage, err:
        print >> sys.stderr, err.msg
        return 2

    else:
        Kraken(path).release()

if __name__ == "__main__":
    sys.exit(main())
