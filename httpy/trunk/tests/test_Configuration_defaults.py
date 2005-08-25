#!/usr/bin/env python

import os
import unittest

from httpy.Configuration import Configuration
from ConfigurationTestCase import ConfigurationTestCase


class TestConfigurationDefaults(unittest.TestCase):

    dict2tuple = staticmethod(ConfigurationTestCase.dict2tuple)

    def buildTestSite(self):
        os.mkdir('root')
        file('root/index.html', 'w')

    def testDefaults(self):
        server = {}
        server['ip'] = ''
        server['port'] = 8080
        server = self.dict2tuple(server)

        handler = {}
        handler['root'] = os.path.realpath('.')
        handler['defaults'] = ('index.html', 'index.pt')
        handler['extensions'] = ('pt',)
        handler['mode'] = 'development'
        handler = self.dict2tuple(handler)

        actual = Configuration()
        self.assertEqual(server, self.dict2tuple(actual.server))
        self.assertEqual(handler, self.dict2tuple(actual.handler))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestConfigurationDefaults))
    return suite

if __name__ == '__main__':
    unittest.main()
