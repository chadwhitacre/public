#!/usr/bin/env python

import os
import unittest

from zope.server.adjustments import default_adj

from httpy.Request import Request

from RequestTestCase import PARTS


class RequestParsesLineTests:
    def testExactLine(self):
        self.request.received(self.LINE)
        expected = self.LINE.strip(),
        actual = self.request.raw_line
        for key,value in things.items():
            self.assertEqual(value,)

class TestRequestParsesLineCRLF(RequestParsesLineTests,unittest.TestCase):
    def setUp(self):
        self.request = Request(default_adj)
        newline='\r\n'
        (self.IE_CRAP,self.LINE,self.HEADERS,self.BODY,self.POST)=PARTS(newline)

class TestRequestParsesLineCR(RequestParsesLineTests,unittest.TestCase):
    def setUp(self):
        self.request = Request(default_adj)
        newline='\r'
        (self.IE_CRAP,self.LINE,self.HEADERS,self.BODY,self.POST)=PARTS(newline)

class TestRequestParsesLineLF(RequestParsesLineTests,unittest.TestCase):
    def setUp(self):
        self.request = Request(default_adj)
        newline='\n'
        (self.IE_CRAP,self.LINE,self.HEADERS,self.BODY,self.POST)=PARTS(newline)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRequestParsesLineCRLF))
    suite.addTest(makeSuite(TestRequestParsesLineCR))
    suite.addTest(makeSuite(TestRequestParsesLineLF))
    return suite

if __name__ == '__main__':
    unittest.main()
