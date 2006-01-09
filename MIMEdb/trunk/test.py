#!/usr/bin/env python
from xmlrpclib import ServerProxy, Error
foo = ServerProxy("http://josemaria:8080/")

print foo

try:
    print foo.ping()
except Error, v:
    print "ERROR", v


from pprint import pprint as pp; import code; code.interact(local=locals())