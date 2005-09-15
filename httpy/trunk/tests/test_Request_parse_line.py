#!/usr/bin/env python

import os
import unittest

from zope.server.adjustments import default_adj

from httpy.Request import Request

from RequestTestCase import PARTS



DUMMY_URI = [ ('fragment','fragment')
            , ('netloc','netloc')
            , ('parameters','parameters')
            , ('path','/path')
            , ('query','query')
            , ('scheme','http')
             ]

class RequestParsesLineTests:

    def testExactLine(self):
        self.request.received(self.LINE)
        things = { 'method': 'POST'
                 , 'path': '/path'
                 , 'uri': DUMMY_URI
                  }
        for key, value in things.items():
            expected = value
            actual = getattr(self.request,key)
            if key == 'uri':
                actual = sorted([i for i in actual.items()])
            self.assertEqual(expected, actual)


class TestRequestParsesLineCRLF(RequestParsesLineTests,unittest.TestCase):
    def setUp(self):
        self.request = Request(default_adj)
        newline='\r\n'
        (self.IE_CRAP,self.LINE,self.LINE2,self.HEADERS,self.HEADERS2,self.BODY,self.POST,self.GET)=PARTS(newline)

class TestRequestParsesLineCR(RequestParsesLineTests,unittest.TestCase):
    def setUp(self):
        self.request = Request(default_adj)
        newline='\r'
        (self.IE_CRAP,self.LINE,self.LINE2,self.HEADERS,self.HEADERS2,self.BODY,self.POST,self.GET)=PARTS(newline)

class TestRequestParsesLineLF(RequestParsesLineTests,unittest.TestCase):
    def setUp(self):
        self.request = Request(default_adj)
        newline='\n'
        (self.IE_CRAP,self.LINE,self.LINE2,self.HEADERS,self.HEADERS2,self.BODY,self.POST,self.GET)=PARTS(newline)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRequestParsesLineCRLF))
    suite.addTest(makeSuite(TestRequestParsesLineCR))
    suite.addTest(makeSuite(TestRequestParsesLineLF))
    return suite

if __name__ == '__main__':
    unittest.main()
