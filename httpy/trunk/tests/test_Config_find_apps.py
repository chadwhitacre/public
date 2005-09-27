#!/usr/bin/env python

import os
import unittest

from httpy.Config import Config

from TestCaseHttpy import TestCaseHttpy


class TestSetApps(TestCaseHttpy):

    siteroot = os.path.realpath('root')

    def buildTestSite(self):
        os.mkdir('root')
        os.mkdir('root/app1')
        os.mkdir('root/app1/__')
        os.mkdir('root/app2')
        os.mkdir('root/app2/__')


    def testSiteHasAppsAndTheyAreFoundAutomatically(self):
        expected = ('/app2', '/app1')
        actual = Config._find_apps(self.siteroot)
        self.assertEqual(expected, actual)

    def testSiteHasNoAppsAndTheyAreNotFoundAutomatically(self):
        self.removeTestSite()
        os.mkdir('root')
        expected = ()
        actual = Config._find_apps(self.siteroot)
        self.assertEqual(expected, actual)

    def testWhatYouThoughtWasAnAppWasntCauseThereWasNoMagicDirectory(self):
        os.rmdir('root/app1/__')
        expected = ('/app2',)
        actual = Config._find_apps(self.siteroot)
        self.assertEqual(expected, actual)

    def testRootHasMagicDirectory(self):
        os.mkdir('root/__')
        expected = ('/app2','/app1','/')
        actual = Config._find_apps(self.siteroot)
        self.assertEqual(expected, actual)

    def testAppsThreeLevelsDeep(self):
        os.mkdir('root/__')
        os.mkdir('root/app2/app3')
        os.mkdir('root/app2/app3/__')
        expected = ('/app2/app3', '/app2', '/app1', '/')
        actual = Config._find_apps(self.siteroot)
        self.assertEqual(expected, actual)



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSetApps))
    return suite

if __name__ == '__main__':
    unittest.main()
