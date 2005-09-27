#!/usr/bin/env python

import os
import unittest

from httpy.Config import ServerConfig
from httpy.Config import ServerConfigError

from TestCaseHttpy import TestCaseHttpy


class TestSetApps(TestCaseHttpy):

    def buildTestSite(self):
        os.mkdir('root')
        os.mkdir('root/app1')
        os.mkdir('root/app1/__')
        os.mkdir('root/app2')
        os.mkdir('root/app2/__')


    # These test the interaction between _find_apps and _validate_apps.

    def testExplicitlySettingAppsOverridesMagic(self):
        self.config = ServerConfig(['-a/app1', '-rroot'])
        expected = ('/app1','/') # Note root is added, however.
        actual = self.config.apps
        self.assertEqual(expected, actual)

    def testRootOnlyAddedIfNotAlreadyThere(self):
        self.config = ServerConfig(['-a/:/app1', '-rroot'])
        expected = ('/','/app1')
        actual = self.config.apps
        self.assertEqual(expected, actual)

    def testCanExplicitlyTurnOffAllApps(self):
        file('httpy.conf', 'w').write('[m]\napps=\n')
        self.config = ServerConfig(['-fhttpy.conf'])
        expected = ('/',) # Can't turn off root app though!
        actual = self.config.apps
        self.assertEqual(expected, actual)


    # These test _validate_apps.

    def testValidateGoodAppsReturnsNone(self):
        self.config = ServerConfig(['-a/app1:/app2', '-rroot'])
        expected = None
        actual = self.config._validate_apps()
        self.assertEqual(expected, actual)

    def testValidateBadAppsRaisesError(self):
        self.config = ServerConfig()
        self.config.apps'] = ['/not-there
        self.assertRaises( ServerConfigError
                         , self.config._validate_apps
                          )

    def testAppWithoutMagicDirectoryRaisesError(self):
        os.rmdir('root/app1/__')
        self.config = ServerConfig(['-rroot'])
        self.config.apps'] = ['/app1
        self.assertRaises( ServerConfigError
                         , self.config._validate_apps
                          )



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSetApps))
    return suite

if __name__ == '__main__':
    unittest.main()
