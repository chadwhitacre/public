#!/usr/bin/env python

import os
import unittest

TestRunner = unittest.TextTestRunner
suite = unittest.TestSuite()

tests = os.listdir(os.curdir)
tests = [n[:-3] for n in tests if n.startswith('test') and n.endswith('.py')]

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

    cleanup()
finally:
    cleanup()
