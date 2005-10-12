#!/usr/bin/env python

import os
import sys
import unittest

from httpy._zope.interface.exceptions import BrokenImplementation
from httpy._zope.interface.exceptions import BrokenMethodImplementation

from httpy.Config import AppConfig
from httpy.Config import ConfigError

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
APP_BAD_INIT = """\
class Application:
    def __init__(self):
        pass
    def process(self, request):
        pass
"""
APP_BAD_PROCESS = """\
class Application:
    def __init__(self, config):
        pass
    def process(self):
        pass
"""


class TestAppConfig(TestCaseHttpy):

    testsite = [  '/app1'
               ,  '/app1/__'
               , ('/app1/__/app.py', DUMMY_APP + "num=1")
               ,  '/app2'
               ,  '/app3'
               ,  '/app3/__'
               , ('/app3/__/app.py', DUMMY_APP + "num=3")
                ]


    def tearDown(self):
        TestCaseHttpy.tearDown(self)
        for app in ('/app1', '/app2'):
            if app in sys.modules:
                del sys.modules[app]

    def testBasic(self):
        config = AppConfig(self.siteroot, '/app1')
        expected = "<httpy app @ /app1 >"
        actual = str(config)
        self.assertEqual(expected, actual)

    def testNoFilesystemRoot(self):
        self.assertRaises( ConfigError
                         , AppConfig
                         , self.siteroot
                         , '/not-there'
                          )

    def testNoMagicDir(self):
        self.assertRaises( ConfigError
                         , AppConfig
                         , self.siteroot
                         , '/app2'
                          )

    def testNoMagicDirForRootGivesDefaultApp(self):
        config = AppConfig(self.siteroot, '/')
        expected = "<default httpy app @ / >"
        actual = str(config)
        self.assertEqual(expected, actual)

    def testMagicDirForRootGivesThatApp(self):
        os.mkdir(os.sep.join(['root', '__']))
        app = open(os.sep.join(['root', '__', 'app.py']), 'w')
        app.write(DUMMY_APP + 'root = True')
        app.close()
        config = AppConfig(self.siteroot, '/')
        self.assert_(config.module.root)

    def testNoAppToImport(self):
        os.remove('root/app1/__/app.py')
        self.assertRaises( ConfigError
                         , AppConfig
                         , self.siteroot
                         , '/app1'
                          )

    def testAppsCanCoexist(self):
        app1 = AppConfig(self.siteroot, '/app1')
        app3 = AppConfig(self.siteroot, '/app3')
        self.assertNotEqual(app1.module.num, app3.module.num)


    # test our zope interface usage

    def testAppNoApplication(self):
        app = open(os.sep.join(['root', 'app1', '__', 'app.py']), 'w')
        app.write(APP_NO_APPLICATION)
        app.close()
        self.assertRaises( BrokenImplementation
                         , AppConfig
                         , self.siteroot
                         , '/app1'
                          )

    def testAppNoProcess(self):
        app = open(os.sep.join(['root', 'app1', '__', 'app.py']), 'w')
        app.write(APP_NO_PROCESS)
        app.close()
        self.assertRaises( BrokenImplementation
                         , AppConfig
                         , self.siteroot
                        , '/app1'
                          )

    def testAppBadInit(self):
        app = open(os.sep.join(['root', 'app1', '__', 'app.py']), 'w')
        app.write(APP_BAD_INIT)
        app.close()
        self.assertRaises( BrokenMethodImplementation
                         , AppConfig
                         , self.siteroot
                         , '/app1'
                          )

    def testAppBadProcess(self):
        app = open(os.sep.join(['root', 'app1', '__', 'app.py']), 'w')
        app.write(APP_BAD_PROCESS)
        app.close()
        self.assertRaises( BrokenMethodImplementation
                         , AppConfig
                         , self.siteroot
                         , '/app1'
                          )




def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAppConfig))
    return suite

if __name__ == '__main__':
    unittest.main()
