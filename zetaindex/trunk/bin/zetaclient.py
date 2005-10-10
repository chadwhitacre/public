#!/usr/bin/env python

from xmlrpclib import ServerProxy()

index = ServerProxy('localhost:5370')

import code; code.interact(local=locals())
