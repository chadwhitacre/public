#!/usr/bin/env python

import os
import unittest

from TestCaseHttpy import TestCaseHttpy


argv_default = [
    '--ip='
  , '--port=8080'
  , '--mode=deployment'
  , '--root=.'
  , '--apps='
  , '--verbosity=1'
   ]

argv_default_plus_path = [
    '--ip='
  , '--port=8080'
  , '--mode=deployment'
  , '--root=.'
  , '--apps='
  , '--verbosity=1'
  , '--file=httpy.conf'
   ]

argv_short_names = [
#   '-i' -- can't specify empty with shorts
    '-p','8080'
  , '-r','.'
  , '-mdeployment'
# , '-a' -- can't specify empty with shorts
  , '-fhttpy.conf'
  , '-v1'
   ]

argv_only_one = [
    '--port=8080'
   ]

argv_extra_options = [
    '--ip='
  , '--port=8080'
  , '--mode=deployment'
  , '--root=.'
  , '--apps='
  , '--verbosity=1'
  , '--file=httpy.conf'
  , '--cheese=yummy'
   ]

class TestConfigOpts(TestCaseHttpy):

    d = {}
    d['ip'] = ''
    d['port'] = 8080
    d['mode'] = 'deployment'
    d['root'] = os.path.realpath('.')
    d['apps'] = ()
    d['verbosity'] = 1

    def testDefaultsAsOptions(self):
        expected = self.dict2tuple(self.d.copy())
        opts, path = self.config._opts(argv_default)
        actual = self.dict2tuple(opts)
        self.assertEqual(expected, actual)
        self.assertEqual('', path)

    def testDefaultsPlusConfigFilePath(self):
        file('httpy.conf', 'w')
        expected = self.dict2tuple(self.d.copy())
        opts, path = self.config._opts(argv_default_plus_path)
        actual = self.dict2tuple(opts)
        self.assertEqual(expected, actual)
        self.assertEqual(os.path.realpath('httpy.conf'), path)

    def testShortNames(self):
        file('httpy.conf', 'w')
        d = self.d.copy()
        del d['ip']
        del d['apps']
        expected = self.dict2tuple(d)
        opts, path = self.config._opts(argv_short_names)
        actual = self.dict2tuple(opts)
        self.assertEqual(expected, actual)
        self.assertEqual(os.path.realpath('httpy.conf'), path)

    def testOnlyOneOption(self):
        file('httpy.conf', 'w')
        d = self.d.copy()
        del d['ip']
        del d['mode']
        del d['root']
        del d['apps']
        del d['verbosity']
        expected = self.dict2tuple(d)
        opts, path = self.config._opts(argv_only_one)
        actual = self.dict2tuple(opts)
        self.assertEqual(expected, actual)
        self.assertEqual('', path)

    def testExtraOptionsRaisesError(self):
        file('httpy.conf', 'w')
        expected = self.dict2tuple(self.d)
        import sys
        from StringIO import StringIO
        sys.stderr = StringIO()
        self.assertRaises( SystemExit
                         , self.config._opts
                         , argv_extra_options
                          )
        sys.stderr = sys.__stderr__



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestConfigOpts))
    return suite

if __name__ == '__main__':
    unittest.main()
