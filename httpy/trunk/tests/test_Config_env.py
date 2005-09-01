#!/usr/bin/env python

import os
import unittest

from ConfigurationTestCase import ConfigurationTestCase
from httpy.Configuration import Configuration

class TestConfigurationEnv(ConfigurationTestCase):

    def testDefaultsAsEnv(self):

        d = {}
        d['ip'] = ''
        d['port'] = 8080
        d['root'] = os.path.realpath('.')
        d['defaults'] = ('index.html', 'index.pt')
        d['extensions'] = ('pt',)
        d['mode'] = 'deployment'

        os.environ['HTTPY_IP'] = ''
        os.environ['HTTPY_PORT'] = '8080'
        os.environ['HTTPY_ROOT'] = '.'
        os.environ['HTTPY_DEFAULTS'] = 'index.html index.pt'
        os.environ['HTTPY_EXTENSIONS'] = 'pt'
        os.environ['HTTPY_MODE'] = 'deployment'

        expected = self.dict2tuple(d)
        actual = self.dict2tuple(self.config._env())

        self.assertEqual(expected, actual)


    def testJustOneValueInEnv(self):

        d = {'port':9000}
        os.environ['HTTPY_PORT'] = '9000'

        expected = self.dict2tuple(d)
        actual = self.dict2tuple(self.config._env())

        self.assertEqual(expected, actual)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestConfigurationEnv))
    return suite

if __name__ == '__main__':
    unittest.main()
