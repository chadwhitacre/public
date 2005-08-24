#!/usr/bin/env python

import os, sys
if __name__ == '__main__':
    sys.path.insert(0, os.path.realpath('..'))

import unittest
TestRunner = unittest.TextTestRunner
suite = unittest.TestSuite()

tests = os.listdir(os.curdir)
tests = [n[:-3] for n in tests if n.startswith('test') and n.endswith('.py')]

for test_ in tests:
    m = __import__(test_)
    if hasattr(m, 'test_suite'):
        suite.addTest(m.test_suite())

if __name__ == '__main__':
    TestRunner().run(suite)