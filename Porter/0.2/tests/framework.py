""" alter sys.path in case we are installed somewhere besides site-packages """
import os, sys

cwd = os.getcwd() # this should be tests/
sep = os.sep
pkg_parent = sep.join(cwd.split(sep)[:-2])
if pkg_parent not in sys.path:
    sys.path.append(pkg_parent)
