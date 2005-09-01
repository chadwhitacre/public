#!/usr/bin/env python

import os
import unittest

from ConfigurationTestCase import ConfigurationTestCase


class TestConfigurationDefaults(ConfigurationTestCase):
    """Put it all together. These test __init__.
    """

    def testDefaults(self):

        # expected -- these are the defaults
        server = {}
        server['ip'] = ''
        server['port'] = 8080
        handler = {}
        handler['root'] = os.path.realpath('.')
        handler['defaults'] = ('index.html', 'index.pt')
        handler['extensions'] = ('pt',)
        handler['mode'] = 'deployment'
        server = self.dict2tuple(server)
        handler = self.dict2tuple(handler)

        actual = self.config

        self.assertEqual(server, self.dict2tuple(actual.server))
        self.assertEqual(handler, self.dict2tuple(actual.handler))


    def testOverlapProperly(self):

        # set up website
        os.mkdir('root')

        # set up environment
        os.environ['HTTPY_MODE'] = 'development' # should be retained
        os.environ['HTTPY_PORT'] = '9000'        # should be overriden

        # set up configuration file
        conf = file('httpy.conf', 'w')
        conf.write(os.linesep.join([
            "[server]"
          , "port: 537"                 # should be retained
          , ""
          , "[handler]"
          , "root = /etc"               # should be overridden
          , "defaults = default.asp"    # should be retained
          , "extensions= asp"           # should be retained
           ]))
        conf.close()

        argv = [ '-r','root'
               , '-f','httpy.conf'
                ]

        # expected
        server = {}
        server['ip'] = ''                               # default
        server['port'] = 537                            # file
        handler = {}
        handler['root'] = os.path.realpath('./root')    # opts
        handler['defaults'] = ('default.asp',)          # file
        handler['extensions'] = ('asp',)                # file
        handler['mode'] = 'development'                 # env
        server = self.dict2tuple(server)
        handler = self.dict2tuple(handler)

        self.config.__init__(argv)
        actual = self.config

        self.assertEqual(server, self.dict2tuple(actual.server))
        self.assertEqual(handler, self.dict2tuple(actual.handler))

        os.rmdir('root')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestConfigurationDefaults))
    return suite

if __name__ == '__main__':
    unittest.main()
