#!/usr/bin/env python

import os
import unittest

from ConfigTestCase import ConfigTestCase
from httpy.Config import Config

class TestConfigEnv(ConfigTestCase):

    def testDefaultsAsEnv(self):

        d = {}
        d['ip'] = ''
        d['port'] = 8080
        d['mode'] = 'deployment'
        d['root'] = os.path.realpath('.')

        os.environ['HTTPY_IP'] = ''
        os.environ['HTTPY_PORT'] = '8080'
        os.environ['HTTPY_MODE'] = 'deployment'
        os.environ['HTTPY_ROOT'] = '.'

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
    suite.addTest(makeSuite(TestConfigEnv))
    return suite

if __name__ == '__main__':
    unittest.main()
