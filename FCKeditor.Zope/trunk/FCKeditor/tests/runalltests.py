#!/usr/bin/env python
"""This script runs all scripts named test*.py in the current directory with the
current python interpreter. We use this instead of ZopeTestCase/runalltests.py
because we don't want to be dependent on ZopeTestCase.
"""

import os, sys

# formatting helpers
C = '#'; SOLID = C*79; EMPTY = '%s%s%s' % (C, ' '*77, C)

def header():
    print
    print SOLID
    print EMPTY
    print '%s  %s  %s' % (C, test.ljust(73), C)
    print EMPTY


def footer():
    print EMPTY
    print SOLID

tests = [n for n in os.listdir('.') if n.startswith('test') and n.endswith('.py')]
for test in tests:
    header()
    os.system('%s %s' % (sys.executable, test))
    footer()

