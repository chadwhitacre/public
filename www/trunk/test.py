#!/usr/bin/env python
from xmlrpclib import Fault
from www import www
result = www().notify('au.DEPLOYED.main')
if isinstance(result, Fault):
    print 'Fault %s' % result.faultCode
    print result.faultString
else:
    print result