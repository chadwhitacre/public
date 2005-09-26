#!/usr/bin/env python

import os
import unittest

from zope.server.adjustments import default_adj
from httpy.Request import ZopeRequest, Response

from utils import REQUEST_PARTS


class RequestParsesLineTests:

    def testThickLine(self):
        line = "GET http://netloc/path;parameters?query#fragment HTTP/1.1"
        self.request.received(line+self.newline)
        things = { 'method': 'GET'
                 , 'path': '/path'
                 , 'uri': { 'fragment':'fragment'
                          , 'netloc':'netloc'
                          , 'parameters':'parameters'
                          , 'path':'/path'
                          , 'query':'query'
                          , 'scheme':'http' }
                  }
        for key, value in things.items():
            expected = value
            actual = getattr(self.request,key)
            self.assertEqual(expected, actual)

    def testThinLine(self):
        line = "GET / HTTP/1.1"
        self.request.received(line+self.newline)
        things = { 'method': 'GET'
                 , 'path': '/'
                 , 'uri': { 'parameters': ''
                          , 'fragment': ''
                          , 'netloc': ''
                          , 'query': ''
                          , 'path': '/'
                          , 'scheme': ''}
                  }
        for key, value in things.items():
            expected = value
            actual = getattr(self.request,key)
            self.assertEqual(expected, actual)

    def testShortLine(self):
        line = "GET /"
        self.request.received(line+self.newline)
        things = { 'method': 'GET'
                 , 'path': '/'
                 , 'uri': { 'parameters': ''
                          , 'fragment': ''
                          , 'netloc': ''
                          , 'query': ''
                          , 'path': '/'
                          , 'scheme': ''}
                  }
        for key, value in things.items():
            expected = value
            actual = getattr(self.request,key)
            self.assertEqual(expected, actual)

    def testPOST(self):
        line = "POST / HTTP/1.1"
        self.request.received(line+self.newline)
        things = { 'method': 'POST'
                 , 'path': '/'
                 , 'uri': { 'parameters': ''
                          , 'fragment': ''
                          , 'netloc': ''
                          , 'query': ''
                          , 'path': '/'
                          , 'scheme': ''}
                  }
        for key, value in things.items():
            expected = value
            actual = getattr(self.request,key)
            self.assertEqual(expected, actual)

    def testHEAD(self):
        line = "HEAD / HTTP/1.1"
        self.request.received(line+self.newline)
        things = { 'method': 'HEAD'
                 , 'path': '/'
                 , 'uri': { 'parameters': ''
                          , 'fragment': ''
                          , 'netloc': ''
                          , 'query': ''
                          , 'path': '/'
                          , 'scheme': ''}
                  }
        for key, value in things.items():
            expected = value
            actual = getattr(self.request,key)
            self.assertEqual(expected, actual)

    def testBadShortLine(self):
        line = "GET"
        try:
            self.request.received(line+self.newline)
        except Response, err:
            self.assertEqual(err.code,400)
            self.assertEqual(err.headers,{})
            self.assertEqual(err.body,\
                            "The Request-Line `%s' appears to be " % line +
                            "malformed because it has neither two nor " +
                            "three tokens.")

    def testBadLongLine(self):
        line = "GET / HTTP/1.1 WTF!?"
        try:
            self.request.received(line+self.newline)
        except Response, err:
            self.assertEqual(err.code,400)
            self.assertEqual(err.headers,{})
            self.assertEqual(err.body,\
                            "The Request-Line `%s' appears to be " % line +
                            "malformed because it has neither two nor " +
                            "three tokens.")

    def testBadMethod(self):
        line = "BAD / HTTP/1.1"
        try:
            self.request.received(line+self.newline)
        except Response, err:
            self.assertEqual(err.code,501)
            self.assertEqual(err.headers,{})
            self.assertEqual(err.body,\
                "This server does not implement the 'BAD' method.")

    def testBadUri(self):
        line = "GET //foo HTTP/1.1"
        try:
            self.request.received(line+self.newline)
        except Response, err:
            self.assertEqual(err.code,400)
            self.assertEqual(err.headers,{})
            self.assertEqual(err.body,'')

    def testBadVersion(self):
        line = "GET /foo WTF/1.1"
        try:
            self.request.received(line+self.newline)
        except Response, err:
            self.assertEqual(err.code,400)
            self.assertEqual(err.headers,{})
            self.assertEqual(err.body,
                             "The HTTP-Version `WTF/1.1' appears to " +
                             "be malformed because it does not match the " +
                             "pattern `^HTTP/\d+\.\d+$'.")


class TestRequestParsesLineCRLF(RequestParsesLineTests,unittest.TestCase):
    def setUp(self):
        self.request = ZopeRequest(default_adj)
        self.newline='\r\n'
        (self.IE_CRAP,self.LINE,self.LINE2,self.HEADERS,self.HEADERS2,self.BODY,self.POST,self.GET)=REQUEST_PARTS(self.newline)

class TestRequestParsesLineCR(RequestParsesLineTests,unittest.TestCase):
    def setUp(self):
        self.request = ZopeRequest(default_adj)
        self.newline='\r'
        (self.IE_CRAP,self.LINE,self.LINE2,self.HEADERS,self.HEADERS2,self.BODY,self.POST,self.GET)=REQUEST_PARTS(self.newline)

class TestRequestParsesLineLF(RequestParsesLineTests,unittest.TestCase):
    def setUp(self):
        self.request = ZopeRequest(default_adj)
        self.newline='\n'
        (self.IE_CRAP,self.LINE,self.LINE2,self.HEADERS,self.HEADERS2,self.BODY,self.POST,self.GET)=REQUEST_PARTS(self.newline)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRequestParsesLineCRLF))
    suite.addTest(makeSuite(TestRequestParsesLineCR))
    suite.addTest(makeSuite(TestRequestParsesLineLF))
    return suite

if __name__ == '__main__':
    unittest.main()
