#!/usr/bin/env python

import os
import unittest
from httplib import HTTPConnection
from httplib import HTTPResponse as ClientHTTPResponse

from httpy.Config import Config
from httpy.Server import Server

from TestCaseHttpy import TestCaseHttpy


class TestServer(TestCaseHttpy):

    server = True
    verbosity = 99

    def buildTestSite(self):
        os.mkdir('root')
        file('root/index.html', 'w').write("Greetings, program!")

    def testBasic(self):
        expected = (1, 0)
        actual = self._server.http_version
        self.assertEqual(expected, actual)

        expected = "HTTP/1.0"
        actual = self._server.http_version_string
        self.assertEqual(expected, actual)

        expected = "httpy/0.5"
        actual = self._server.response_header
        self.assertEqual(expected, actual)

    def testRoundTrip(self):
        conn = HTTPConnection('localhost', self.port)
        conn.request("GET", "/", '', {'Accept':'text/plain'})
        expected = "Greetings, program!"
        actual = conn.getresponse().read()
        self.assertEqual(expected, actual)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestServer))
    return suite

if __name__ == '__main__':
    unittest.main()
