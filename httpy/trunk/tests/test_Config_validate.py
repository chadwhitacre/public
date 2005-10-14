#!/usr/bin/env python

import os
import unittest

from httpy.Config import Config
from httpy.Config import ConfigError

from TestCaseHttpy import TestCaseHttpy


class TestConfigValidate(TestCaseHttpy):

    want_config = True

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

    def testIPErrorMessage(self):
        d = {'ip':'256.68.1.1'}
        try:
            self.config._validate('test', d)
        except ConfigError, err:
            expected = "Found bad IP `256.68.1.1' in context `test'. IP " +\
                       "must be empty or a valid IPv4 address."
            actual = err.msg
            self.assertEqual(expected, actual)


    # port
    # ====

    def testGoodPort(self):
        d = {'port':8080}
        expected = d.copy()
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)

    def testOutOfRangeRaisesError(self):
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test', {'port':100000}
                          )
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test', {'port':65536}
                          )
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test', {'port':-1}
                          )
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test', {'port':-8080}
                          )

    def testButInRangeIsFine(self):
        d = {'port':0}
        expected = d.copy()
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)

        d = {'port':1}
        expected = d.copy()
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)

        d = {'port':80}
        expected = d.copy()
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)

        d = {'port':65535}
        expected = d.copy()
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)

    def testDigitStringIsCoerced(self):
        d = {'port':'8080'}
        expected = {'port':8080}
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)

    def testNonIntableRaisesError(self):
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test', {'port':False} # considered non-intable here
                          )
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test', {'port':[]}
                          )
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test', {'port':['foo']}
                          )
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test', {'port':None}
                          )

    def testPortErrorMessage(self):
        d = {'port':None}
        try:
            self.config._validate('test', d)
        except ConfigError, err:
            expected = "Found bad port `None' in context `test'. Port " +\
                       "must be an integer between 0 and 65535."
            actual = err.msg
            self.assertEqual(expected, actual)


    # mode
    # ====

    def testGoodMode(self):
        d = {'mode':'deployment'}
        expected = d.copy()
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)

    def testDevelopmentMode(self):
        d = {'mode':'development'}
        expected = d.copy()
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)

    def testDebuggingMode(self):
        d = {'mode':'debugging'}
        expected = d.copy()
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)

    def testUniqueAbbreviationsWorkDeployment(self):
        good_abbreviations = ( 'deploymen'
                             , 'deployme'
                             , 'deploym'
                             , 'deploy'
                             , 'deplo'
                             , 'depl'
                             , 'dep'
                              )
        for abb in good_abbreviations:
            expected = {'mode':'deployment'}
            actual = self.config._validate('test', {'mode':abb})
            self.assertEqual(expected, actual)

    def testUniqueAbbreviationsWorkDevelopment(self):
        good_abbreviations = ( 'developmen'
                             , 'developme'
                             , 'developm'
                             , 'develop'
                             , 'develo'
                             , 'devel'
                             , 'deve'
                             , 'dev'
                              )
        for abb in good_abbreviations:
            expected = {'mode':'development'}
            actual = self.config._validate('test', {'mode':abb})
            self.assertEqual(expected, actual)

    def testUniqueAbbreviationsWorkDebugging(self):
        good_abbreviations = ( 'debuggin'
                             , 'debuggi'
                             , 'debugg'
                             , 'debug'
                             , 'debu'
                             , 'deb'
                              )
        for abb in good_abbreviations:
            expected = {'mode':'debugging'}
            actual = self.config._validate('test', {'mode':abb})
            self.assertEqual(expected, actual)

    def testNonUniqueAbbreviationsFail(self):
        for abb in ('de', 'd'):
            self.assertRaises( ConfigError
                             , self.config._validate
                             , 'test', {'mode':abb}
                              )

    def testAnythingElseRaisesError(self):
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test', {'mode':'$pt'}
                          )
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test', {'mode':0}
                          )
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test', {'mode':'developmental'}
                          )
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test', {'mode':'-*- Python -*-'}
                          )
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test', {'mode':False}
                          )
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test', {'mode':0755}
                          )

    def testModeErrorMessage(self):
        d = {'mode':None}
        try:
            self.config._validate('test', d)
        except ConfigError, err:
            expected = ("Found bad mode `None' in context `test'. Mode must " +
                        "be either `deployment,' `development' or " +
                        "`debugging.' Abbreviations are fine.")
            actual = err.msg
            self.assertEqual(expected, actual)


    # root
    # ====

    def testGoodRoot(self):
        d = {'root':'.'}
        expected = {'root':os.path.realpath('.')}
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)

    def testNonDirectoryRootRaisesError(self):
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test', {'root':'./runalltests.py'}
                          )

    def testNonExistantRootAlsoRaisesError(self):
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test', {'root':'./not-there'}
                          )

    def testRootErrorMessage(self):
        d = {'root':None}
        try:
            self.config._validate('test', d)
        except ConfigError, err:
            expected = "Found bad root `None' in context `test'. Root " +\
                       "must point to a directory."
            actual = err.msg
            self.assertEqual(expected, actual)


    # apps
    # ====

    def testGoodApps(self):
        d = {'apps':('/app1', '/app2')}
        expected = {'apps':('/app1', '/app2')}
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)

    def testStringCoercedToTuple(self):
        d = {'apps':'/app1:/app2'}
        expected = {'apps':('/app1', '/app2')}
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)

    def testDefaultsErrorMessage(self):
        d = {'apps':None}
        try:
            self.config._validate('test', d)
        except ConfigError, err:
            expected = ("Found bad apps `None' in context `test'. Apps " +
                        "must be a colon-separated list of paths rooted in " +
                        "the website root.")
            actual = err.msg
            self.assertEqual(expected, actual)


    # verbosity
    # =========

    def testGoodVerbosity(self):
        d = {'verbosity':1}
        expected = d.copy()
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)

    def testVerbosityOutOfRangeRaisesError(self):
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test', {'verbosity':100000}
                          )
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test', {'verbosity':100}
                          )
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test', {'verbosity':-1}
                          )
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test', {'verbosity':-100000}
                          )

    def testButVerbosityInRangeIsFine(self):
        d = {'verbosity':0}
        expected = d.copy()
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)

        d = {'verbosity':1}
        expected = d.copy()
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)

        d = {'verbosity':49}
        expected = d.copy()
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)

        d = {'verbosity':99}
        expected = d.copy()
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)

    def testVerbosityDigitStringIsCoerced(self):
        d = {'verbosity':'1'}
        expected = {'verbosity':1}
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)

    def testNonIntableVerbosityRaisesError(self):
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test', {'verbosity':False} # considered non-intable
                                                       # here
                          )
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test', {'verbosity':[]}
                          )
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test', {'verbosity':['foo']}
                          )
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test', {'verbosity':None}
                          )

    def testVerbosityErrorMessage(self):
        d = {'verbosity':None}
        try:
            self.config._validate('test', d)
        except ConfigError, err:
            expected = ("Found bad verbosity `None' in context `test'. " +
                        "Verbosity must be an integer between 0 and 99.")
            actual = err.msg
            self.assertEqual(expected, actual)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestConfigValidate))
    return suite

if __name__ == '__main__':
    unittest.main()
