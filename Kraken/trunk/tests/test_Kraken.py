#!/usr/bin/env python

import os
import unittest

from KrakenTestCase import KrakenTestCase


dummy_from = 'From: Chad Whitacre <chad.whitacre@zetaweb.com>'


class TestKraken(KrakenTestCase):

    def testFromAddr(self):
        expected = 'chad.whitacre@zetaweb.com'
        actual = self.kraken.from_addr(test_str=dummy_from)
        self.assertEqual(expected, actual)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestKraken))
    return suite

if __name__ == '__main__':
    unittest.main()
