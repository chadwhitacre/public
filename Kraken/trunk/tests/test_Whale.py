#!/usr/bin/env python

import os
import unittest

from KrakenTestCase import KrakenTestCase


class TestWhale(KrakenTestCase):

    def testAddrs(self):
        expected = ['chad@zetaweb.com']
        actual = self.whale.addrs('whale/to.addrs')
        self.assertEqual(expected, actual)

    def testAddrs2(self):
        expected = [ 'chad@zetaweb.com'
                   , 'whit537@gmail.com'
                   , 'info@zetaweb.com'
                    ]
        actual = self.whale.addrs('whale/from.addrs')
        self.assertEqual(expected, actual)

    def testAddrs0(self):
        file('whale/to.addrs','w')
        expected = []
        actual = self.whale.addrs('whale/to.addrs')
        self.assertEqual(expected, actual)

    def testSendTo(self):
        expected = ['chad@zetaweb.com']
        actual = self.whale.send_to
        self.assertEqual(expected, actual)

    def testAcceptFrom(self):
        expected = [ 'chad@zetaweb.com'
                   , 'whit537@gmail.com'
                   , 'info@zetaweb.com'
                    ]
        actual = self.whale.accept_from
        self.assertEqual(expected, actual)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestWhale))
    return suite

if __name__ == '__main__':
    unittest.main()
