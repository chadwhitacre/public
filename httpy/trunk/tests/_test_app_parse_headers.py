#!/usr/bin/env python

import os
import unittest

from httpy.Request import ZopeRequest
from zope.server.adjustments import default_adj
from TestCaseRequest import PARTS
from email.Message import Message

class RequestParseHeadersTests:
        
    def testMessageIsMessage(self):
        self.assert_(isinstance(self.message,Message))
        
    def testMessageHasRightContents(self):
        things={
            'Host': 'josemaria:5370',
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.10) Gecko/20050716 Firefox/1.0.6',
            'Accept': 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
            'Accept-Language': 'en-us,en;q=0.7,ar;q=0.3',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            'Keep-Alive': '300',
            'Connection': 'keep-alive',
            'Referer': 'http://www.zetadev.com/tmp/test.html',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': '8',
            }
        for key, value in things.items():
            self.assertEqual(value,self.message.get(key))
            
class TestRequestParseHeadersCRLF(RequestParseHeadersTests,unittest.TestCase):
    def setUp(self):
        self.rr = Request(default_adj)
        newline='\r\n'
        self.IE_CRAP,self.LINE,self.HEADERS,self.BODY,self.POST=PARTS(newline)
        self.rr.received(self.LINE)
        self.rr.received(self.HEADERS)
        self.message = self.rr.message
        
class TestRequestParseHeadersCR(RequestParseHeadersTests,unittest.TestCase):
    def setUp(self):
        self.rr = Request(default_adj)
        newline='\r'
        self.IE_CRAP,self.LINE,self.HEADERS,self.BODY,self.POST=PARTS(newline)
        self.rr.received(self.LINE)
        self.rr.received(self.HEADERS)
        self.message = self.rr.message
        
class TestRequestParseHeadersLF(RequestParseHeadersTests,unittest.TestCase):
    def setUp(self):
        self.rr = Request(default_adj)
        newline='\n'
        self.IE_CRAP,self.LINE,self.HEADERS,self.BODY,self.POST=PARTS(newline)
        self.rr.received(self.LINE)
        self.rr.received(self.HEADERS)
        self.message = self.rr.message

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRequestParseHeadersCRLF))
    suite.addTest(makeSuite(TestRequestParseHeadersCR))
    suite.addTest(makeSuite(TestRequestParseHeadersLF))
    return suite

if __name__ == '__main__':
    unittest.main()
