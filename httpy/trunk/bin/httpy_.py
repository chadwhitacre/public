#!/usr/local/bin/python
"""httpy -- a straightforward Python webserver. `man 1 httpy' for details.
"""
import sys

from httpy.couplers.standalone import StandAlone
from httpy.couplers.standalone.utils import ConfigError, configure
from httpy.responders.static import Static


try:
    address, threads, uid = configure()
except ConfigError, err:
    print >> sys.stderr, err.msg
    print >> sys.stderr, "`man 1 httpy' for usage."
    raise SystemExit(2)

coupled = StandAlone(Static, address, threads, uid)
coupled.go()
