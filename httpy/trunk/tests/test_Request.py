#!/usr/bin/env python

import os
import unittest

#from RequestTestCase import RequestTestCase
RequestTestCase = unittest.TestCase

from httpy.Request import Request

POST = '\r\n'.join([
      "POST / HTTP/1.1"
    , "Host: josemaria:5370"
    , "User-Agent: Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.10) Gecko/20050716 Firefox/1.0.6"
    , "Accept: text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5"
    , "Accept-Language: en-us,en;q=0.7,ar;q=0.3"
    , "Accept-Encoding: gzip,deflate"
    , "Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7"
    , "Keep-Alive: 300"
    , "Connection: keep-alive"
    , "Referer: http://www.zetadev.com/tmp/test.html"
    , "Content-Type: application/x-www-form-urlencoded"
    , "Content-Length: 8"
    , ""
    , "foo=test"
     ])

from zope.server.adjustments import default_adj

class TestRequest(RequestTestCase):

    def setUp(self):
        self.request = Request(default_adj)

    def testPostHasBody(self):
        self.request.received(POST)
        expected = 'foot=test'
        actual = self.request.raw_body
        self.assertEqual(expected, actual)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRequest))
    return suite

if __name__ == '__main__':
    unittest.main()
