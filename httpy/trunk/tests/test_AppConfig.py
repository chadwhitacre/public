#!/usr/bin/env python

import os
import unittest

from httpy._zope.interface.exceptions import BrokenImplementation
from httpy._zope.interface.exceptions import BrokenMethodImplementation

from httpy.Config import AppConfig
from httpy.Config import ConfigError

from TestCaseHttpy import TestCaseHttpy
from utils import DUMMY_APP


APP_NO_TRANSACTION = """\
class Transactien:
    pass
"""
APP_NO_PROCESS = """\
class Transaction:
    pass
"""
APP_BAD_INIT = """\
class Transaction:
    def __init__(self):
        pass
    def process(self, request):
        pass
"""
APP_BAD_PROCESS = """\
class Transaction:
    def __init__(self, config):
        pass
    def process(self):
        pass
"""


class TestAppConfig(TestCaseHttpy):

    def setUp(self):
        TestCaseHttpy.setUp(self)

    def buildTestSite(self):
        os.mkdir('root')
        os.mkdir('root/app1')
        os.mkdir('root/app1/__')
        file('root/app1/__/app.py','w').write(DUMMY_APP)
        os.mkdir('root/app2')


    siteroot = os.path.realpath('root')

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

    def testNoAppToImport(self):
        os.remove('root/app1/__/app.py')
        self.assertRaises( BrokenImplementation
                         , AppConfig
                         , self.siteroot
                         , '/app1'
                          )

    def testAppNoTransaction(self):
        file('root/app1/__/app.py','w').write(APP_NO_TRANSACTION)
        self.assertRaises( BrokenImplementation
                         , AppConfig
                         , self.siteroot
                         , '/app1'
                          )

    def testAppNoProcess(self):
        file('root/app1/__/app.py','w').write(APP_NO_PROCESS)
        self.assertRaises( BrokenImplementation
                         , AppConfig
                         , self.siteroot
                         , '/app1'
                          )

    def testAppBadInit(self):
        file('root/app1/__/app.py','w').write(APP_BAD_INIT)
        self.assertRaises( BrokenMethodImplementation
                         , AppConfig
                         , self.siteroot
                         , '/app1'
                          )

    def testAppBadProcess(self):
        file('root/app1/__/app.py','w').write(APP_BAD_PROCESS)
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
