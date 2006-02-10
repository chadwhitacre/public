#!/usr/bin/env python

import os
import sys
import unittest
from StringIO import StringIO


# prevent logging output; unittest output goes to stderr
__stdout = sys.stdout
sys.stdout = StringIO()


# decide which tests to run
arg = sys.argv[1:2]
prefix = 'test'
if arg:
    prefix = '%s_%s' % (prefix, arg[0])
tests = []
for test_ in os.listdir(os.curdir):
    if test_.startswith(prefix) and test_.endswith('.py'):
        if prefix != 'test':
            print '  ', test_
        tests.append(test_[:-3])
sys.stdout.flush()


# collect and run tests
try:
    TestRunner = unittest.TextTestRunner
    suite = unittest.TestSuite()
    for test_ in tests:
        m = __import__(test_)
        if hasattr(m, 'test_suite'):
            suite.addTest(m.test_suite())
    TestRunner().run(suite)
finally:
    # yucky *.pyc's
    pycs = os.listdir(os.curdir)
    pycs = [n for n in pycs if n.endswith('.pyc')]
    for pyc in pycs:
        os.remove(pyc)
