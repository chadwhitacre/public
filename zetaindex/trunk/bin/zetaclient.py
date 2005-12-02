#!/usr/bin/env python

from xmlrpclib import ServerProxy

index = ServerProxy('http://localhost:5370/')

import code; code.interact(local=locals())
