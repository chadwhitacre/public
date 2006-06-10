"""Alter sys.path to pick up the bin/porter.py script as a module.
"""
import os
import sys

pkg = os.path.realpath('../bin')
if pkg not in sys.path:
    sys.path.append(pkg)
