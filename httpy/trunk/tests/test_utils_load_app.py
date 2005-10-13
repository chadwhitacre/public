#!/usr/bin/env python

import os
import sys
import unittest

from httpy.utils import load_app
from httpy._zope.interface.exceptions import BrokenImplementation
from httpy._zope.interface.exceptions import BrokenMethodImplementation

from TestCaseHttpy import TestCaseHttpy
from utils import DUMMY_APP


APP_NO_APPLICATION = """\
class Applicatien:
    pass
"""
APP_NO_PROCESS = """\
class Application:
    pass
"""
APP_BAD_PROCESS = """\
class Application:
    def __init__(self, config):
        pass
    def respond(self):
        pass
"""


class Testload_app(TestCaseHttpy):

    testsite = [  '/app1'
               ,  '/app1/__'
               , ('/app1/__/app.py', DUMMY_APP + "    num=1")
               ,  '/app2'
               ,  '/app3'
               ,  '/app3/__'
               , ('/app3/__/app.py', DUMMY_APP + "    num=3")
                ]


    def tearDown(self):
        TestCaseHttpy.tearDown(self)
        for app in ('/app1', '/app2'):
            if app in sys.modules:
                del sys.modules[app]

    def testBasic(self):
        config = load_app(self.siteroot, '/app1')
        expected = "</app1.Application instance at" # 0x84aa66c>"
        actual = str(config)
        self.assert_(actual.startswith(expected))

    def testNoFilesystemRoot(self):
        self.assertRaises( StandardError
                         , load_app
                         , self.siteroot
                         , '/not-there'
                          )

    def testNoMagicDir(self):
        self.assertRaises( StandardError
                         , load_app
                         , self.siteroot
                         , '/app2'
                          )

    def testNoMagicDirForRootGivesDefaultApp(self):
        config = load_app(self.siteroot, '/')
        expected = "<default httpy app>"
        actual = str(config)
        self.assertEqual(expected, actual)

    def testMagicDirForRootGivesThatApp(self):
        os.mkdir(os.sep.join(['root', '__']))
        app = open(os.sep.join(['root', '__', 'app.py']), 'w')
        app.write(DUMMY_APP + 'root = True')
        app.close()
        config = load_app(self.siteroot, '/')
        self.assert_(config.site_root)

    def testNoAppToImport(self):
        os.remove('root/app1/__/app.py')
        self.assertRaises( ImportError
                         , load_app
                         , self.siteroot
                         , '/app1'
                          )

    def testAppsCanCoexist(self):
        app1 = load_app(self.siteroot, '/app1')
        app3 = load_app(self.siteroot, '/app3')
        self.assertNotEqual(app1.num, app3.num)


    # test our zope interface usage

    def testAppNoload_app(self):
        app = open(os.sep.join(['root', 'app1', '__', 'app.py']), 'w')
        app.write(APP_NO_APPLICATION)
        app.close()
        self.assertRaises( BrokenImplementation
                         , load_app
                         , self.siteroot
                         , '/app1'
                          )

    def testAppNoProcess(self):
        app = open(os.sep.join(['root', 'app1', '__', 'app.py']), 'w')
        app.write(APP_NO_PROCESS)
        app.close()
        self.assertRaises( BrokenImplementation
                         , load_app
                         , self.siteroot
                        , '/app1'
                          )

    def testAppBadProcess(self):
        app = open(os.sep.join(['root', 'app1', '__', 'app.py']), 'w')
        app.write(APP_BAD_PROCESS)
        app.close()
        self.assertRaises( BrokenMethodImplementation
                         , load_app
                         , self.siteroot
                         , '/app1'
                          )




def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(Testload_app))
    return suite

if __name__ == '__main__':
    unittest.main()
