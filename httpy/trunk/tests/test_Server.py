#!/usr/bin/env python

import os
import unittest

from httpy.Config import Config
from httpy.Server import Server


class TestServer(unittest.TestCase):

    def setUp(self):
        config = Config()
        self.server = Server(config)

    def testBasic(self):
        expected = (1, 1)
        actual = self.server.http_version
        self.assertEqual(expected, actual)

        expected = "HTTP/1.0"
        actual = self.server.http_version_string
        self.assertEqual(expected, actual)

        expected = "httpy/0.5"
        actual = self.server.response_header
        self.assertEqual(expected, actual)


    # not too much to test here, pretty thin wrapper around SocketServer



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestServer))
    return suite

if __name__ == '__main__':
    unittest.main()
