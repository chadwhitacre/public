#!/usr/bin/env python

import os
import unittest

from ConfigurationTestCase import ConfigurationTestCase


class TestConfigurationDefaults(ConfigurationTestCase):
    """Put it all together. This test __init__
    """

    def test(self):

        # expected -- these are the defaults
        server = {}
        server['ip'] = ''
        server['port'] = 8080
        handler = {}
        handler['root'] = os.path.realpath('.')
        handler['defaults'] = ('index.html', 'index.pt')
        handler['extensions'] = ('pt',)
        handler['mode'] = 'development'
        server = self.dict2tuple(server)
        handler = self.dict2tuple(handler)

        actual = self.config

        self.assertEqual(server, self.dict2tuple(actual.server))
        self.assertEqual(handler, self.dict2tuple(actual.handler))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestConfigurationDefaults))
    return suite

if __name__ == '__main__':
    unittest.main()
