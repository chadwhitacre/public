#!/usr/bin/env python

import os
import unittest

from httpy.Request import Request
from RequestTestCase import PARTS

from zope.server.adjustments import default_adj

class RequestGetBodyTests:

    def testExactLineHeadersBody(self):
        self.rr.received(self.LINE)
        self.rr.received(self.HEADERS)
        self.rr.received(self.BODY)
        self.assert_(self.rr.raw_line==self.LINE.strip())
        self.assert_(self.rr.raw_headers==self.HEADERS.strip())
        self.assert_(self.rr.raw_body==self.BODY.strip())
        
    def testLineHeadersBodyAtOnce(self):
        self.rr.received(self.LINE+self.HEADERS+self.BODY)
        self.assert_(self.rr.raw_line==self.LINE.strip())
        self.assert_(self.rr.raw_headers==self.HEADERS.strip())
        self.assert_(self.rr.raw_body==self.BODY.strip())
        
    def testDividedBody(self):
        self.rr.received(self.LINE+self.HEADERS+self.BODY[:4])
        self.rr.received(self.BODY[4:])
        self.assert_(self.rr.raw_line==self.LINE.strip())
        self.assert_(self.rr.raw_headers==self.HEADERS.strip())
        self.assert_(self.rr.raw_body==self.BODY.strip())
        
    def testWholePost(self):
        self.rr.received(self.POST)
        self.assert_(self.rr.raw_line==self.LINE.strip())
        self.assert_(self.rr.raw_headers==self.HEADERS.strip())
        self.assert_(self.rr.raw_body==self.BODY.strip())

        
class TestRequestGetBodyCRLF(RequestGetBodyTests,unittest.TestCase):
    def setUp(self):
        self.rr = Request(default_adj)
        newline='\r\n'
        (self.IE_CRAP,self.LINE,self.HEADERS,self.BODY,self.POST)=PARTS(newline)

class TestRequestGetsBodyCR(RequestGetBodyTests,unittest.TestCase):
    def setUp(self):
        self.rr = Request(default_adj)
        newline='\r'
        (self.IE_CRAP,self.LINE,self.HEADERS,self.BODY,self.POST)=PARTS(newline)

class TestRequestGetsBodyLF(RequestGetBodyTests,unittest.TestCase):
    def setUp(self):
        self.rr = Request(default_adj)
        newline='\n'
        (self.IE_CRAP,self.LINE,self.HEADERS,self.BODY,self.POST)=PARTS(newline)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRequestGetBodyCRLF))
    suite.addTest(makeSuite(TestRequestGetsBodyCR))
    suite.addTest(makeSuite(TestRequestGetsBodyLF))
    return suite

if __name__ == '__main__':
    unittest.main()
