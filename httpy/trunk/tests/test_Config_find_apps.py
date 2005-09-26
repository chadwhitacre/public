#!/usr/bin/env python

import os
import unittest

from httpy.Config import Config

from TestCaseHttpy import TestCaseHttpy


class TestSetApps(TestCaseHttpy):

    def buildTestSite(self):
        os.mkdir('root')
        os.mkdir('root/app1')
        os.mkdir('root/app1/__')
        os.mkdir('root/app2')
        os.mkdir('root/app2/__')


    def testSiteHasAppsAndTheyAreFoundAutomatically(self):
        config = Config()
        expected = ('/app1', '/app2')
        actual = config._find_apps('root')
        self.assertEqual(expected, actual)

    def testSiteHasNoAppsAndTheyAreNotFoundAutomatically(self):
        self.removeTestSite()
        os.mkdir('root')
        config = Config()
        expected = ()
        actual = config._find_apps('root')
        self.assertEqual(expected, actual)

    def testWhatYouThoughtWasAnAppWasntCauseThereWasNoMagicDirectory(self):
        os.rmdir('root/app1/__')
        config = Config()
        expected = ('/app2',)
        actual = config._find_apps('root')
        self.assertEqual(expected, actual)



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSetApps))
    return suite

if __name__ == '__main__':
    unittest.main()
