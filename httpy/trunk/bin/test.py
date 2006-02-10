#!/usr/bin/env python
"""This is a test runner for the httpy library.

Usage, e.g.:

    $ python bin/test.py site-packages/httpy/couplers

The argument to test.py is a path constraint. This runner looks for all tests/
directories under the path constraint, recursing into subdirectories. Within
those directories, it looks for files named test_*.py, and adds the return value
of test_suite within those files to its list of tests to run.

"""
import optparse
import os
import sys
import unittest
from StringIO import StringIO


# Prevent logging output; unittest output goes to stderr.
# =======================================================

__stdout = sys.stdout
sys.stdout = StringIO()


# Get the top of the tree.
# ========================

argv = sys.argv[1:2]
recursive = False
if '-r' in argv:
    recursive = True
    argv.remove('-r')
arg = argv and argv[0] or '.'
root = os.path.realpath(arg)

print recursive
print root
raise SystemExit



# Walk the tree and gather tests.
# ===============================

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
