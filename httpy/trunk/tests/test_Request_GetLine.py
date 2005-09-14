#!/usr/bin/env python

import os
import unittest

from httpy.Request import Request
from zope.server.adjustments import default_adj
from RequestTestCase import PARTS

class RequestGetsLineTests:
    def testExactLine(self):
        self.rr.recieved(self.LINE)
        self.assert_(self.rr.raw_line==self.LINE.strip())
        
    def testShortLine(self):
        short = self.LINE[:4]
        self.rr.recieved(short)
        self.assert_(self.rr.raw_line==None)
        self.assert_(self.rr._tmp==short)
        
    def testDividedLine(self):
        beginning=self.LINE[:4]
        end=self.LINE[4:]
        self.rr.recieved(beginning)
        self.rr.recieved(end)
        self.assert_(self.rr.raw_line==self.LINE.strip())
        
    def testCrappyIELine(self):
        self.rr.recieved(self.IE_CRAP+self.LINE)
        self.assert_(self.rr.raw_line==self.LINE.strip())
        
    def testExtraStuffOnEnd(self):
        self.rr.recieved(self.IE_CRAP+self.LINE+self.HEADERS[:-1])
        self.assert_(self.rr.raw_line==self.LINE.strip())
        self.assert_(self.rr._tmp==self.HEADERS[:-1])
        
    def testAll(self):
        beginning=self.LINE[:4]
        end=self.LINE[4:]
        self.rr.recieved(self.IE_CRAP+beginning)
        self.rr.recieved(end+self.HEADERS[:-1])
        self.assert_(self.rr.raw_line==self.LINE.strip())
        self.assert_(self.rr._tmp==self.HEADERS[:-1])

class TestRequestGetsLineCRLF(RequestGetsLineTests,unittest.TestCase):
    def setUp(self):
        self.rr = Request(default_adj)
        newline='\r\n'
        (self.IE_CRAP,self.LINE,self.HEADERS,self.BODY,self.POST)=PARTS(newline)
        
class TestRequestGetsLineCR(RequestGetsLineTests,unittest.TestCase):
    def setUp(self):
        self.rr = Request(default_adj)
        newline='\r'
        (self.IE_CRAP,self.LINE,self.HEADERS,self.BODY,self.POST)=PARTS(newline)

class TestRequestGetsLineLF(RequestGetsLineTests,unittest.TestCase):
    def setUp(self):
        self.rr = Request(default_adj)
        newline='\n'
        (self.IE_CRAP,self.LINE,self.HEADERS,self.BODY,self.POST)=PARTS(newline)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRequestGetsLineCR))
    suite.addTest(makeSuite(TestRequestGetsLineCRLF))
    suite.addTest(makeSuite(TestRequestGetsLineLF))
    return suite

if __name__ == '__main__':
    unittest.main()
