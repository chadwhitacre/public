#!/usr/bin/env python

import os
import unittest

from httpy.Config import ServerConfig

from TestCaseHttpy import TestCaseHttpy
from utils import DUMMY_APP


class TestFindApps(TestCaseHttpy):

    testsite = [  '/app1'
               ,  '/app1/__'
               , ('/app1/__/app.py', DUMMY_APP)
               ,  '/app2'
               ,  '/app2/__'
               , ('/app1/__/app.py', DUMMY_APP)
                ]

    def testSiteHasAppsAndTheyAreFoundAutomatically(self):
        expected = ('/app2', '/app1')
        actual = ServerConfig._find_apps(self.siteroot)
        self.assertEqual(expected, actual)

    def testSiteHasNoAppsAndTheyAreNotFoundAutomatically(self):
        self.removeTestSite()
        os.mkdir('root')
        expected = ()
        actual = ServerConfig._find_apps(self.siteroot)
        self.assertEqual(expected, actual)

    def testWhatYouThoughtWasAnAppWasntCauseThereWasNoMagicDirectory(self):
        os.remove('root/app1/__/app.py')
        os.rmdir('root/app1/__')
        expected = ('/app2',)
        actual = ServerConfig._find_apps(self.siteroot)
        self.assertEqual(expected, actual)

    def testRootHasMagicDirectory(self):
        os.mkdir('root/__')
        expected = ('/app2', '/app1', '/')
        actual = ServerConfig._find_apps(self.siteroot)
        self.assertEqual(expected, actual)

    def testAppsThreeLevelsDeep(self):
        os.mkdir('root/__')
        os.mkdir('root/app2/app3')
        os.mkdir('root/app2/app3/__')
        expected = ('/app2/app3', '/app2', '/app1', '/')
        actual = ServerConfig._find_apps(self.siteroot)
        self.assertEqual(expected, actual)

    def testAppsBelowAMagicDirAreNotFound(self):
        os.mkdir('root/__')
        os.mkdir('root/__/app3')
        os.mkdir('root/__/app3/__')
        expected = ('/app2', '/app1', '/')
        actual = ServerConfig._find_apps(self.siteroot)
        self.assertEqual(expected, actual)


    # Here are some tests from the front.

    def testExplicitlySettingAppsOverridesMagic(self):
        self.config = ServerConfig(['-a/app1', '-rroot'])
        expected = [os.path.realpath('root/app1/__'), None]
        actual = [a.__ for a in self.config.apps]
        self.assertEqual(expected, actual)

    def testRootOnlyAddedIfNotAlreadyThere(self):
        self.config = ServerConfig(['-a/:/app1', '-rroot'])
        expected = [None, os.path.realpath('root/app1/__')]
        actual = [a.__ for a in self.config.apps]
        self.assertEqual(expected, actual)

    def testCanExplicitlyTurnOffAllApps(self):
        file('httpy.conf', 'w').write('[m]\napps=\n')
        self.config = ServerConfig(['-fhttpy.conf'])
        expected = [None] # Can't turn off root app though!
        actual = [a.__ for a in self.config.apps]
        self.assertEqual(expected, actual)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFindApps))
    return suite

if __name__ == '__main__':
    unittest.main()
