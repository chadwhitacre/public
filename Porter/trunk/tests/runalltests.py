"""

Runs all tests in the current directory

Execute like:
   python runalltests.py

This was lifted from CMFPlone/tests

"""

import os, sys
if __name__ == '__main__':
    import framework

import unittest
TestRunner = unittest.TextTestRunner
suite = unittest.TestSuite()

tests = os.listdir(os.curdir)
tests = [n[:-3] for n in tests if n.startswith('test') and n.endswith('.py')]

for test in tests:
    m = __import__(test)
    if hasattr(m, 'test_suite'):
        suite.addTest(m.test_suite())

if __name__ == '__main__':
    TestRunner().run(suite)
