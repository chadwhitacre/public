#!/usr/bin/env python

import os
import unittest

from TestCaseConfig import TestCaseConfig


class TestConfigDefaults(TestCaseConfig):

    def testDefaults(self):

        d = {}
        d['ip'] = ''
        d['port'] = 8080
        d['mode'] = 'deployment'
        d['root'] = os.path.realpath('.')
        d['apps'] = ()
        d['verbosity'] = 1

        expected = self.dict2tuple(d)
        actual = self.dict2tuple(self.config._defaults())

        self.assertEqual(expected, actual)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestConfigDefaults))
    return suite

if __name__ == '__main__':
    unittest.main()
