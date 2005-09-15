#!/usr/bin/env python

import os
import unittest

from zope.server.adjustments import default_adj

from httpy.Request import Request

from RequestTestCase import PARTS


class RequestGetBodyTests:

    def testExactLineHeadersBody(self):
        self.request.received(self.LINE)
        self.request.received(self.HEADERS)
        self.request.received(self.BODY)
        self.assertEqual(self.request.line, self.LINE.strip())
        self.assertEqual(self.request.headers, self.HEADERS.strip())
        self.assertEqual(self.request.body, self.BODY.strip())

    def testLineHeadersBodyAtOnce(self):
        self.request.received(self.LINE+self.HEADERS+self.BODY)
        self.assertEqual(self.request.line, self.LINE.strip())
        self.assertEqual(self.request.headers, self.HEADERS.strip())
        self.assertEqual(self.request.body, self.BODY.strip())

    def testDividedBody(self):
        self.request.received(self.LINE+self.HEADERS+self.BODY[:4])
        self.request.received(self.BODY[4:])
        self.assertEqual(self.request.line, self.LINE.strip())
        self.assertEqual(self.request.headers, self.HEADERS.strip())
        self.assertEqual(self.request.body, self.BODY.strip())

    def testWholePost(self):
        self.request.received(self.POST)
        self.assertEqual(self.request.line, self.LINE.strip())
        self.assertEqual(self.request.headers, self.HEADERS.strip())
        self.assertEqual(self.request.body, self.BODY.strip())

    def testWholeGet(self):
        self.request.received(self.GET)
        self.assertEqual(self.request.line, self.LINE2.strip())
        self.assertEqual(self.request.headers, self.HEADERS2.strip())
        self.assertEqual(self.request.body, '')


class TestRequestGetBodyCRLF(RequestGetBodyTests,unittest.TestCase):
    def setUp(self):
        self.request = Request(default_adj)
        newline='\r\n'
        (self.IE_CRAP,self.LINE,self.LINE2,self.HEADERS,self.HEADERS2,self.BODY,self.POST,self.GET)=PARTS(newline)

class TestRequestGetsBodyCR(RequestGetBodyTests,unittest.TestCase):
    def setUp(self):
        self.request = Request(default_adj)
        newline='\r'
        (self.IE_CRAP,self.LINE,self.LINE2,self.HEADERS,self.HEADERS2,self.BODY,self.POST,self.GET)=PARTS(newline)

class TestRequestGetsBodyLF(RequestGetBodyTests,unittest.TestCase):
    def setUp(self):
        self.request = Request(default_adj)
        newline='\n'
        (self.IE_CRAP,self.LINE,self.LINE2,self.HEADERS,self.HEADERS2,self.BODY,self.POST,self.GET)=PARTS(newline)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRequestGetBodyCRLF))
    suite.addTest(makeSuite(TestRequestGetsBodyCR))
    suite.addTest(makeSuite(TestRequestGetsBodyLF))
    return suite

if __name__ == '__main__':
    unittest.main()
