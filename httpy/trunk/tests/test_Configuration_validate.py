#!/usr/bin/env python

import os
import unittest

from ConfigurationTestCase import ConfigurationTestCase


class TestConfiguration(ConfigurationTestCase):

    def buildTestSite(self):
        os.mkdir('root')
        file('root/index.html', 'w')

    def testEmptyDictReturned(self):
        expected = {}
        actual = self.config._validate('foo', {})
        self.assertEqual(expected, actual)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestConfiguration))
    return suite

if __name__ == '__main__':
    unittest.main()
