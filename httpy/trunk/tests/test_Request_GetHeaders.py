#!/usr/bin/env python

import os
import unittest

from httpy.Request import Request
from RequestTestCase import PARTS

from zope.server.adjustments import default_adj

class RequestGetHeadersTests:
    def testExactLine(self):
        self.rr.recieved(self.LINE)
        self.rr.recieved(self.HEADERS)
        self.assert_(self.rr.raw_line==self.LINE.strip())
        self.assert_(self.rr.raw_headers==self.HEADERS.strip())
        
    def testLineHeadersAtOnce(self):
        self.rr.recieved(self.LINE+self.HEADERS)
        self.assert_(self.rr.raw_line==self.LINE.strip())
        self.assert_(self.rr.raw_headers==self.HEADERS.strip())
    
    def testPartialHeaders(self):
        self.rr.recieved(self.LINE+self.HEADERS[:30])
        self.assert_(self.rr.raw_line==self.LINE.strip())
        self.assert_(self.rr._tmp==self.HEADERS[:30])
        self.assert_(self.rr.raw_headers==None)
        
    def testDividedHeaders(self):
        self.rr.recieved(self.LINE+self.HEADERS[:30])
        self.rr.recieved(self.HEADERS[30:])
        self.assert_(self.rr.raw_line==self.LINE.strip())
        self.assert_(self.rr.raw_headers==self.HEADERS.strip())
        
    def testExtraStuff(self):
        self.rr.recieved(self.POST)
        self.assert_(self.rr.raw_line==self.LINE.strip())
        self.assert_(self.rr.raw_headers==self.HEADERS.strip())

    def testDividedHeadersAndExtra(self):
        self.rr.recieved(self.LINE+self.HEADERS[:30])
        self.rr.recieved(self.HEADERS[30:]+self.BODY)
        self.assert_(self.rr.raw_line==self.LINE.strip())
        self.assert_(self.rr.raw_headers==self.HEADERS.strip())
        
class TestRequestGetHeadersCRLF(RequestGetHeadersTests,unittest.TestCase):
    def setUp(self):
        self.rr = Request(default_adj)
        newline='\r\n'
        (self.IE_CRAP,self.LINE,self.HEADERS,self.BODY,self.POST)=PARTS(newline)
        
class TestRequestGetsHeadersCR(RequestGetHeadersTests,unittest.TestCase):
    def setUp(self):
        self.rr = Request(default_adj)
        newline='\r'
        (self.IE_CRAP,self.LINE,self.HEADERS,self.BODY,self.POST)=PARTS(newline)

class TestRequestGetsHeadersLF(RequestGetHeadersTests,unittest.TestCase):
    def setUp(self):
        self.rr = Request(default_adj)
        newline='\n'
        (self.IE_CRAP,self.LINE,self.HEADERS,self.BODY,self.POST)=PARTS(newline)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRequestGetHeadersCRLF))
    suite.addTest(makeSuite(TestRequestGetsHeadersCR))
    suite.addTest(makeSuite(TestRequestGetsHeadersLF))
    return suite

if __name__ == '__main__':
    unittest.main()
