#!/usr/bin/env python

import os
import sys
import unittest

os.environ['HTTPY_VERBOSITY'] = '0'

TestRunner = unittest.TextTestRunner
suite = unittest.TestSuite()

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

def cleanup():
    pycs = os.listdir(os.curdir)
    pycs = [n for n in pycs if n.endswith('.pyc')]
    for pyc in pycs:
        os.remove(pyc)

try:
    for test_ in tests:
        m = __import__(test_)
        if hasattr(m, 'test_suite'):
            suite.addTest(m.test_suite())

    if __name__ == '__main__':
        TestRunner().run(suite)

finally:
    cleanup()
