#!/usr/bin/env python

import os
import unittest

from ConfigurationTestCase import ConfigurationTestCase


class TestConfigurationDefaults(ConfigurationTestCase):

    def testDefaults(self):

        d = {}
        d['ip'] = ''
        d['port'] = 8080
        d['root'] = os.path.realpath('.')
        d['defaults'] = ('index.html', 'index.pt')
        d['extensions'] = ('pt',)
        d['mode'] = 'deployment'

        expected = self.dict2tuple(d)
        actual = self.dict2tuple(self.config._defaults())

        self.assertEqual(expected, actual)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestConfigurationDefaults))
    return suite

if __name__ == '__main__':
    unittest.main()
