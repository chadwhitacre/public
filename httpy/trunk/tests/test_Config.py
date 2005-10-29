#!/usr/bin/env python

import os
import unittest

from httpy.Config import Config

from TestCaseHttpy import TestCaseHttpy


class TestConfigDefaults(TestCaseHttpy):
    """Put it all together. These test __init__.
    """

    def testDefaults(self):

        d = {}
        d['sockfam'] = 2 # socket.AF_INET
        d['address'] = ('', 8080)
        d['root'] = os.path.realpath('.')
        d['apps'] = [None]

        e = {}
        e['HTTPY_MODE'] = 'deployment'
        e['HTTPY_VERBOSITY'] = '1'

        config = Config()

        for k, expected in d.items():
            if k == 'apps':
                continue
            actual = getattr(config, k)
            self.assertEqual(expected, actual)
        self.assertEqual([a.__ for a in config.apps], d['apps'])

        for k, expected in e.items():
            actual = os.environ[k]
            self.assertEqual(expected, actual)


    def testOverlapProperly(self):

        # set up environment
        os.environ['HTTPY_MODE'] = 'development' # should be retained
        os.environ['HTTPY_PORT'] = '9000'       # should be overriden
        os.environ['HTTPY_VERBOSITY'] = '99'    # should be retained

        # set up configuration file
        conf = file('httpy.conf', 'w')
        conf.write(os.linesep.join([
            "[main]"
          , "address: :537"                     # should be retained
          , "root = /etc"                       # should be overridden
           ]))
        conf.close()

        argv = [ '-r','root'                    # should be retained
              , '-f','httpy.conf'              # should be retained
                ]

        # expected
        d = {}
        d['sockfam'] = 2                        # default
        d['address'] = ('', 537)                # file
        d['root'] = os.path.realpath('./root')  # opts
        d['apps'] = [None]                      # default

        e = {}
        e['HTTPY_MODE'] = 'development'         # env
        e['HTTPY_VERBOSITY'] = '99'             # env

        config = Config(argv)

        for k, expected in d.items():
            if k == 'apps':
                continue
            actual = getattr(config, k)
            self.assertEqual(expected, actual)
        self.assertEqual([a.__ for a in config.apps], d['apps'])

        for k, expected in e.items():
            actual = os.environ[k]
            self.assertEqual(expected, actual)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestConfigDefaults))
    return suite

if __name__ == '__main__':
    unittest.main()
