#!/usr/bin/env python

import os
import unittest

from zope.server.adjustments import default_adj

from httpy.Request import Request

from RequestTestCase import PARTS


class RequestGetsLineTests:

    def testExactLine(self):
        self.request.received(self.LINE)
        self.assert_(self.request.line==self.LINE.strip())

    def testShortLine(self):
        short = self.LINE[:4]
        self.request.received(short)
        self.assert_(self.request.line==None)
        self.assert_(self.request._tmp==short)

    def testDividedLine(self):
        beginning=self.LINE[:4]
        end=self.LINE[4:]
        self.request.received(beginning)
        self.request.received(end)
        self.assert_(self.request.line==self.LINE.strip())

    def testCrappyIELine(self):
        self.request.received(self.IE_CRAP+self.LINE)
        self.assert_(self.request.line==self.LINE.strip())

    def testExtraStuffOnEnd(self):
        self.request.received(self.IE_CRAP+self.LINE+self.HEADERS[:-1])
        self.assert_(self.request.line==self.LINE.strip())
        self.assert_(self.request._tmp==self.HEADERS[:-1])

    def testAll(self):
        beginning=self.LINE[:4]
        end=self.LINE[4:]
        self.request.received(self.IE_CRAP+beginning)
        self.request.received(end+self.HEADERS[:-1])
        self.assert_(self.request.line==self.LINE.strip())
        self.assert_(self.request._tmp==self.HEADERS[:-1])

class TestRequestGetsLineCRLF(RequestGetsLineTests,unittest.TestCase):
    def setUp(self):
        self.request = Request(default_adj)
        newline='\r\n'
        (self.IE_CRAP,self.LINE,self.HEADERS,self.BODY,self.POST)=PARTS(newline)

class TestRequestGetsLineCR(RequestGetsLineTests,unittest.TestCase):
    def setUp(self):
        self.request = Request(default_adj)
        newline='\r'
        (self.IE_CRAP,self.LINE,self.HEADERS,self.BODY,self.POST)=PARTS(newline)

class TestRequestGetsLineLF(RequestGetsLineTests,unittest.TestCase):
    def setUp(self):
        self.request = Request(default_adj)
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
