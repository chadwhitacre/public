#!/usr/bin/env python

import os
import socket
import unittest

from httpy.Config import Config
from httpy.Config import ConfigError

from TestCaseHttpy import TestCaseHttpy


class TestConfigValidate(TestCaseHttpy):

    want_config = True


    # AF_UNIX
    # =======

    def testGoodAF_UNIX(self):
        self.config.sockfam = socket.AF_UNIX
        addr = expected = '/var/run/foo.socket'
        actual = self.config._validate_address(addr)
        self.assertEqual(expected, actual)

    def testAnyDumbStringWillWork(self):
        self.config.sockfam = socket.AF_UNIX
        import string
        addr = expected = string.printable
        actual = self.config._validate_address(addr)
        self.assertEqual(expected, actual)

    def testButNothingElseWill(self):
        self.config.sockfam = socket.AF_UNIX
        self.assertRaises( ConfigError
                         , self.config._validate_address
                         , (192.16811,8080)
                          )
        self.assertRaises( ConfigError
                         , self.config._validate_address
                         , ('192.168.1.1', 8080)
                          )
        self.assertRaises( ConfigError
                         , self.config._validate_address
                         , None
                          )


    # AF_INET
    # =======

    def testIPv4CoercionFromString(self):
        self.config.sockfam = socket.AF_INET
        addr = '192.168.1.1:8080'
        expected = ('192.168.1.1', 8080)
        actual = self.config._validate_address(addr)
        self.assertEqual(expected, actual)

    def testWeDontAcceptHostnamesOnlyNumericIPAddresses(self):
        self.config.sockfam = socket.AF_INET
        addr = expected = ('foo.example.com', 8080)
        self.assertRaises( ConfigError
                         , self.config._validate_address
                         , addr
                          )


    # ip

    def testGoodIPv4(self):
        self.config.sockfam = socket.AF_INET
        addr = ('192.168.1.1', 8080)
        expected = ('192.168.1.1', 8080)
        actual = self.config._validate_address(addr)
        self.assertEqual(expected, actual)

    def testIPOutOfRange(self):
        self.config.sockfam = socket.AF_INET
        addr = ('256.68.1.1', 8080)
        self.assertRaises( ConfigError
                         , self.config._validate_address
                         , addr
                          )

    def testNonFalseIPOfWrongTypeRaisesError(self):
        self.config.sockfam = socket.AF_INET
        self.assertRaises( ConfigError
                         , self.config._validate_address
                         , (192.16811,8080)
                          )
        self.assertRaises( ConfigError
                         , self.config._validate_address
                         , (('192','168','1','1'), 8080)
                          )
        self.assertRaises( ConfigError
                         , self.config._validate_address
                         , ({'192':'168','1':'1'}, 8080)
                          )
        self.assertRaises( ConfigError
                         , self.config._validate_address
                         , (['192','168','1','1'], 8080)
                          )

    def testIPErrorMessage(self):
        self.config.sockfam = socket.AF_INET
        try:
            self.config._validate_address((None, 8080))
        except ConfigError, err:
            expected = ("Found bad address `(None, 8080)' for address " +
                        "family `AF_INET'.")
            actual = err.msg
            self.assertEqual(expected, actual)


    # port
    # ====

    def testGoodPort(self):
        addr = ('', 8080)
        expected = ('', 8080)
        self.config.sockfam = socket.AF_INET
        actual = self.config._validate_address(addr)
        self.assertEqual(expected, actual)

    def testOutOfRangeRaisesError(self):
        self.config.sockfam = socket.AF_INET
        self.assertRaises( ConfigError
                         , self.config._validate_address
                         , ('', 100000)
                          )
        self.assertRaises( ConfigError
                         , self.config._validate_address
                         , ('', 65536)
                          )
        self.assertRaises( ConfigError
                         , self.config._validate_address
                         , ('', -1)
                          )
        self.assertRaises( ConfigError
                         , self.config._validate_address
                         , ('', -8080)
                          )

    def testButInRangeIsFine(self):
        self.config.sockfam = socket.AF_INET
        addr = expected = ('',0)
        actual = self.config._validate_address(addr)
        self.assertEqual(expected, actual)

        addr = expected = ('',1)
        actual = self.config._validate_address(addr)
        self.assertEqual(expected, actual)

        addr = expected = ('',80)
        actual = self.config._validate_address(addr)
        self.assertEqual(expected, actual)

        addr = expected = ('',65535)
        actual = self.config._validate_address(addr)
        self.assertEqual(expected, actual)

    def testDigitStringIsCoerced(self):
        self.config.sockfam = socket.AF_INET
        addr = ('', '8080')
        expected = ('', 8080)
        actual = self.config._validate_address(addr)
        self.assertEqual(expected, actual)

    def testNonIntableRaisesError(self):
        self.config.sockfam = socket.AF_INET
        self.assertRaises( ConfigError
                         , self.config._validate_address
                         , ('', False) # considered non-intable here
                          )
        self.assertRaises( ConfigError
                         , self.config._validate_address
                         , ('', [])
                          )
        self.assertRaises( ConfigError
                         , self.config._validate_address
                         , ('', ['foo'])
                          )
        self.assertRaises( ConfigError
                         , self.config._validate_address
                         , ('', None)
                          )

    def testPortErrorMessage(self):
        self.config.sockfam = socket.AF_INET
        try:
            self.config._validate_address(('', None))
        except ConfigError, err:
            expected = ("Found bad address `('', None)' for address " +
                        "family `AF_INET'.")
            actual = err.msg
            self.assertEqual(expected, actual)


    # AF_INET6
    # ========

    def testAF_INET6SomeDay(self):
        self.config.sockfam = socket.AF_INET6
        self.assertRaises( NotImplementedError
                         , self.config._validate_address
                         , '3ffe:ffff:0:f101::1/64'
                          )




def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestConfigValidate))
    return suite

if __name__ == '__main__':
    unittest.main()
