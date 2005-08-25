#!/usr/bin/env python

import os
import unittest

from ConfigurationTestCase import ConfigurationTestCase
from httpy.Configuration import ConfigError

class TestConfiguration(ConfigurationTestCase):

    def buildTestSite(self):
        os.mkdir('root')
        file('root/index.html', 'w')

    # Basic functions
    # ===============

    def testEmptyDictReturned(self):
        expected = {}
        actual = self.config._validate('test', {})
        self.assertEqual(expected, actual)

    def testSuperfluousKeysRemoved(self):
        d = {'ip':'', 'foo':'bar'}
        expected = {'ip':''}
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)

    def testErrorMessagesMakeItOut(self):
        d = {'ip':'256.68.1.1'}
        try:
            self.config._validate('test', d)
        except ConfigError, err:
            expected = "Found bad IP '256.68.1.1' in context 'test'. IP " +\
                       "must be empty or a valid IPv4 address."
            actual = err.msg
            self.assertEqual(expected, actual)


    # ip
    # ==

    def testGoodIP(self):
        d = {'ip':'192.168.1.1'}
        expected = d.copy()
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)

    def testIPOutOfRange(self):
        d = {'ip':'256.68.1.1'}
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test'
                         , d
                          )

    def testFalseIPCoercedToEmptyString(self):
        d = {'ip':''}
        expected = {'ip':''}
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)

        d = {'ip':None}
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)

        d = {'ip':[]}
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)

        d = {'ip':tuple()}
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)

        d = {'ip':{}}
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)

        d = {'ip':False}
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)

        d = {'ip':0}
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)


    def testNonFalseIPOfWrongTypeRaisesError(self):
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test'
                         , {'ip':192.16811}
                          )
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test'
                         , {'ip':('192','168','1','1')}
                          )
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test'
                         , {'ip':{'192':'168','1':'1'}}
                          )
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test'
                         , {'ip':['192','168','1','1']}
                          )


    # port
    # ====

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestConfiguration))
    return suite

if __name__ == '__main__':
    unittest.main()
