#!/usr/bin/env python

import os
import unittest

from ConfigTestCase import ConfigTestCase


class TestConfigDefaults(ConfigTestCase):
    """Put it all together. These test __init__.
    """

    def testDefaults(self):

        d = {}
        d['ip'] = ''
        d['port'] = 8080
        d['root'] = os.path.realpath('.')
        d['mode'] = 'deployment'
        d['apps'] = ('/',)
        d['verbosity'] = 1

        expected = self.dict2tuple(d)
        actual = self.dict2tuple(self.config)

        self.assertEqual(expected, actual)


    def testOverlapProperly(self):

        # set up website
        if os.path.isdir('root'):
            os.rmdir('root')
        os.mkdir('root')

        # set up environment
        os.environ['HTTPY_MODE'] = 'development' # should be retained
        os.environ['HTTPY_PORT'] = '9000'       # should be overriden
        os.environ['HTTPY_VERBOSITY'] = '99'    # should be retained

        # set up configuration file
        conf = file('httpy.conf', 'w')
        conf.write(os.linesep.join([
            "[main]"
          , "port: 537"                         # should be retained
          , "root = /etc"                       # should be overridden
           ]))
        conf.close()

        argv = [ '-r','root'                    # should be retained
               , '-f','httpy.conf'              # should be retained
                ]

        # expected
        d = {}
        d['ip'] = ''                            # default
        d['port'] = 537                         # file
        d['root'] = os.path.realpath('./root')  # opts
        d['mode'] = 'development'               # env
        d['apps'] = ('/',)                      # default
        d['verbosity'] = 99                     # env

        expected = self.dict2tuple(d)
        self.config.__init__(argv)
        actual = self.dict2tuple(self.config)

        self.assertEqual(expected, actual)

        os.rmdir('root')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestConfigDefaults))
    return suite

if __name__ == '__main__':
    unittest.main()
