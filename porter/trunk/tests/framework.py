# we need to insert ourselves into sys.path so that our test driver can find us

import os, sys
curdir = sys.path[0]
sep = os.sep
our_location = sep.join(curdir.split(sep)[:-2])
sys.path.insert(0,our_location)
