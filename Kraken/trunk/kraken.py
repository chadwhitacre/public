#!/usr/bin/env python

from kraken.Kraken import Kraken

class Usage(Exception):
    def __init__(self, msg=''):
        self.msg = msg
        Exception.__init__()


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    try:
        if len(argv) != 1:
            raise Usage()
        path = os.path.realpath(argv[0])
        if not os.path.isdir(path):
            raise Usage("%s does not point to a directory." % path)

    except Usage, err:
        print >> sys.stderr, err.msg
        #print >> sys.stderr, "kraken takes a single argument, the path to " +\
        #                     "an address file."
        return 2

    else:
        Kraken(path).release()

if __name__ == "__main__":
    sys.exit(main())
