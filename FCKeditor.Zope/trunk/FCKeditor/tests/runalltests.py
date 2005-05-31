#BOILERPLATE###################################################################
#                                                                             #
#  This package wraps FCKeditor for use in the Zope web application server.   #
#  Copyright (C) 2005 Chad Whitacre <http://www.zetadev.com/>                 #
#                                                                             #
#  This library is free software; you can redistribute it and/or modify it    #
#  under the terms of the GNU Lesser General Public License as published by   #
#  the Free Software Foundation; either version 2.1 of the License, or (at    #
#  your option) any later version.                                            #
#                                                                             #
#  This library is distributed in the hope that it will be useful, but        #
#  WITHOUT ANY WARRANTY; without even the implied warranty of                 #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser    #
#  General Public License for more details.                                   #
#                                                                             #
#  You should have received a copy of the GNU Lesser General Public License   #
#  along with this library; if not, write to the Free Software Foundation,    #
#  Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA                #
#                                                                             #
###################################################################BOILERPLATE#
#
# Runs all tests in the current directory [and below]
#
# Execute like:
#   python runalltests.py [-R]
#
# Alternatively use the testrunner:
#   python /path/to/Zope/bin/testrunner.py -qa
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest, imp
TestRunner = unittest.TextTestRunner
suite = unittest.TestSuite()

def visitor(recursive, dir, names):
    tests = [n[:-3] for n in names if n.startswith('test') and n.endswith('.py')]

    for test in tests:
        saved_syspath = sys.path[:]
        sys.path.insert(0, dir)
        try:
            fp, path, desc = imp.find_module(test, [dir])
            m = imp.load_module(test, fp, path, desc)
            if hasattr(m, 'test_suite'):
                suite.addTest(m.test_suite())
        finally:
            fp.close()
            sys.path[:] = saved_syspath

    if not recursive:
        names[:] = []

if __name__ == '__main__':
    os.path.walk(os.curdir, visitor, '-R' in sys.argv)
    TestRunner().run(suite)

