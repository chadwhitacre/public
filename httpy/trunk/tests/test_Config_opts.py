#!/usr/bin/env python

import os
import unittest

from ConfigurationTestCase import ConfigurationTestCase


argv_default = [
    '--ip='
  , '--port=8080'
  , '--root=.'
  , '--defaults=index.html,index.pt'
  , '--extensions=pt'
  , '--mode=deployment'
   ]

argv_default_path = [
    '--ip='
  , '--port=8080'
  , '--root=.'
  , '--defaults=index.html,index.pt'
  , '--extensions=pt'
  , '--mode=deployment'
  , '--file=httpy.conf'
   ]


argv_short_names = [ # can't specify empty with shorts
    '-p','8080'
  , '-r','.'
  , '-d','index.html,index.pt'
  , '-ept'
  , '-mdeployment'
  , '-fhttpy.conf'
   ]


class TestConfigurationOpts(ConfigurationTestCase):

    d = {}
    d['ip'] = ''
    d['port'] = 8080
    d['root'] = os.path.realpath('.')
    d['defaults'] = ('index.html', 'index.pt')
    d['extensions'] = ('pt',)
    d['mode'] = 'deployment'

    def testDefaultsAsOptions(self):
        expected = self.dict2tuple(self.d.copy())
        opts, path = self.config._opts(argv_default)
        actual = self.dict2tuple(opts)
        self.assertEqual(expected, actual)
        self.assertEqual('', path)

    def testDefaultsPlusConfigFilePath(self):
        file('httpy.conf', 'w')
        expected = self.dict2tuple(self.d.copy())
        opts, path = self.config._opts(argv_default_path)
        actual = self.dict2tuple(opts)
        self.assertEqual(expected, actual)
        self.assertEqual(os.path.realpath('httpy.conf'), path)

    def testShortNames(self):
        file('httpy.conf', 'w')
        d = self.d.copy()
        del d['ip']
        expected = self.dict2tuple(d)
        opts, path = self.config._opts(argv_short_names)
        actual = self.dict2tuple(opts)
        self.assertEqual(expected, actual)
        self.assertEqual(os.path.realpath('httpy.conf'), path)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestConfigurationOpts))
    return suite

if __name__ == '__main__':
    unittest.main()
