#!/usr/bin/env python

import os
import unittest

from TestCaseHttpy import TestCaseHttpy
from httpy.Config import Config

class TestCase(TestCaseHttpy):

    want_config = True

    def testDefaultsAsEnv(self):

        self.scrubenv()

        d = {}
        d['ip'] = ''
        d['port'] = 8080
        d['mode'] = 'deployment'
        d['root'] = os.path.realpath('.')
        d['apps'] = ()
        d['verbosity'] = 1

        os.environ['HTTPY_IP'] = ''
        os.environ['HTTPY_PORT'] = '8080'
        os.environ['HTTPY_MODE'] = 'deployment'
        os.environ['HTTPY_ROOT'] = '.'
        os.environ['HTTPY_APPS'] = ''
        os.environ['HTTPY_VERBOSITY'] = '1'

        expected = self.dict2tuple(d)
        actual = self.dict2tuple(self.config._env())

        self.assertEqual(expected, actual)

    def testJustOneExtraValueInEnv(self):

        self.scrubenv()
        d = {'port':9000}
        os.environ['HTTPY_PORT'] = '9000'

        expected = self.dict2tuple(d)
        actual = self.dict2tuple(self.config._env())

        self.assertEqual(expected, actual)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCase))
    return suite

if __name__ == '__main__':
    unittest.main()
