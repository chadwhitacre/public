#!/usr/bin/env python

import imp
import os
import unittest

from zope.interface.exceptions import BrokenImplementation
from zope.interface.exceptions import BrokenMethodImplementation

from httpy.AppCache import AppCache
from httpy.NicolasLehuen import Entry
from httpy import DefaultApp

from TestCaseHttpy import TestCaseHttpy


APP_BASE = """\
class Transaction:
    def __init__(self, config):
        pass
    def process(self, request):
        raise "heck"
"""

APP0 = APP_BASE + "appnum = 0"
APP1 = APP_BASE + "appnum = 1"
APP2 = APP_BASE + "appnum = 2"


APP_NO__INIT__ = """\
class Transaction:
    def process(self, request):
        raise "heck"
"""
APP_NO_PROCESS = """\
class Transaction:
    def __init__(self, config):
        pass
"""
APP_BAD__INIT__ = """\
class Transaction:
    def __init__(self):
        pass
    def process(self, request):
        raise "heck"
"""
APP_BAD_PROCESS = """\
class Transaction:
    def __init__(self, config):
        pass
    def process(self):
        raise "heck"
"""

class TestAppCache(TestCaseHttpy):

    def setUp(self):
        TestCaseHttpy.setUp(self)
        self.apps = AppCache('development')

    def buildTestSite(self):
        os.mkdir('root')
        os.mkdir('root/__')
        file('root/__/app.py','w').write(APP0)
        os.mkdir('root/app1')
        os.mkdir('root/app1/__')
        file('root/app1/__/app.py','w').write(APP1)
        os.mkdir('root/app2')
        os.mkdir('root/app2/__')
        file('root/app2/__/app.py','w').write(APP2)


    # demonstration
    # =============

    def testAttrAccess(self):
        # inner dict is initially empty
        self.assertEqual(self.apps._dict.keys(), [])

        # simple access will return the object and prime the cache
        app = self.apps['root/__']
        self.assertEqual(app.appnum, 0)
        self.assertEqual(self.apps._dict.keys(), ['root/__'])


    # get_app
    # =======

    def testGetApp(self):
        fp, pathname, description = imp.find_module('app', ['root/__'])
        expected = imp.load_module('app', fp, pathname, description)
        import sys
        del(sys.modules['app'])
        os.remove('root/__/app.pyc')

        actual = self.apps.get_app('root/__')
        self.assertEqual(expected.appnum, actual.appnum)

    def testMagicDirectoryIsNone(self):
        expected = DefaultApp
        actual = self.apps.get_app(None)
        self.assertEqual(expected, actual)

    def testTwoModulesBothGetImported(self):
        app1 = self.apps.get_app('root/app1/__')
        self.assertEqual(app1.appnum, 1)
        app2 = self.apps.get_app('root/app2/__')
        self.assertEqual(app2.appnum, 2)

    def testImportErrorRaisesButGetsCleanedUp(self):
        self.assertRaises(ImportError, self.apps.get_app, '/app3/__')
        import sys
        self.assert_('app3/__' not in sys.path)
        self.assert_('app' not in sys.modules)



    # check
    # =====

    def testCheckDepModeUnloadedGetsLoaded(self):
        entry = Entry('root/__')
        self.apps.dev_mode = False
        self.assertEqual(self.apps._dict, {})

        expected = self.apps.get_app('root/__')
        os.remove('root/__/app.pyc')
        actual = self.apps.check('root/__', entry)
        self.assertEqual(expected.appnum, actual.appnum)

    def testCheckDepModeLoadedNotReloaded(self):
        entry = Entry('root/__')
        entry.loaded = True
        self.apps.dev_mode = False

        expected = None
        actual = self.apps.check('root/__', entry)
        self.assertEqual(expected, actual)

    def testCheckDevModeLoadedGetsReloaded(self):
        entry = Entry('root/__')
        entry.loaded = True
        self.apps.dev_mode = True

        expected = self.apps.get_app('root/__')
        os.remove('root/__/app.pyc')
        actual = self.apps.check('root/__', entry)
        self.assertEqual(expected.appnum, actual.appnum)



    # build
    # =====
    # Since our dummy apps don't explicitly assert that they implement the
    # required interfaces, this also tests tentative=True.

    def testAppNoInit(self):
        entry = Entry('root/__')
        file('root/__/app.py','w').write(APP_NO__INIT__)
        app = self.apps.get_app('root/__')
        self.assertRaises( BrokenImplementation
                         , self.apps.build
                         , 'root/__'
                         , app
                         , entry
                          )

    def testAppNoProcess(self):
        entry = Entry('root/__')
        file('root/__/app.py','w').write(APP_NO_PROCESS)
        app = self.apps.get_app('root/__')
        self.assertRaises( BrokenImplementation
                         , self.apps.build
                         , 'root/__'
                         , app
                         , entry
                          )

    def testAppBadInit(self):
        entry = Entry('root/__')
        file('root/__/app.py','w').write(APP_BAD__INIT__)
        app = self.apps.get_app('root/__')
        self.assertRaises( BrokenMethodImplementation
                         , self.apps.build
                         , 'root/__'
                         , app
                         , entry
                          )

    def testAppBadProcess(self):
        entry = Entry('root/__')
        file('root/__/app.py','w').write(APP_BAD_PROCESS)
        app = self.apps.get_app('root/__')
        self.assertRaises( BrokenMethodImplementation
                         , self.apps.build
                         , 'root/__'
                         , app
                         , entry
                          )


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAppCache))
    return suite

if __name__ == '__main__':
    unittest.main()
