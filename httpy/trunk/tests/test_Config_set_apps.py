#!/usr/bin/env python

import os
import unittest

from httpy.Config import Config

from ConfigTestCase import ConfigTestCase


class TestSetApps(ConfigTestCase):

    def testSiteHasAppsAndTheyAreFoundAutomatically(self):
        self.config = Config()
        expected = ('/app1', '/app2')
        actual = self.config['apps']
        self.assertEqual(expected, actual)

    def testSiteHasNoAppsAndTheyAreNotFoundAutomatically(self):
        self.tearDown()
        self.config = Config()
        expected = ()
        actual = self.config['apps']
        self.assertEqual(expected, actual)

    def testWhatYouThoughtWasAnAppWasntCauseThereWasNoMagicDirectory(self):
        os.rmdir(os.path.join('app1','__'))
        self.config = Config()
        expected = ('/app2',)
        actual = self.config['apps']
        self.assertEqual(expected, actual)

    def testExplicitlySettingAppsOverridesMagic(self):
        self.config = Config(['-a/app1'])
        expected = ('/app1',)
        actual = self.config['apps']
        self.assertEqual(expected, actual)

    def testCanExplicitlyTurnOffAllApps(self):
        file('httpy.conf', 'w').write('[m]\napps=\n')
        self.config = Config(['-fhttpy.conf'])
        expected = ()
        actual = self.config['apps']
        self.assertEqual(expected, actual)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSetApps))
    return suite

if __name__ == '__main__':
    unittest.main()
