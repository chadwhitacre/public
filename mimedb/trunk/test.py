#!/usr/bin/env python
from xmlrpclib import ServerProxy, Error
foo = ServerProxy("http://localhost:5370/")

print foo

try:
    print foo.ping()
except Error, v:
    print "ERROR", v


from pprint import pprint as pp; import code; code.interact(local=locals())