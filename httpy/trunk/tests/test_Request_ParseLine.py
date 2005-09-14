#!/usr/bin/env python

import os
import unittest

from httpy.Request import Request
from zope.server.adjustments import default_adj
from RequestTestCase import PARTS


class RequestParsesLineTests:
    def testExactLine(self):
        self.rr.received(self.LINE)
        things={
        'raw_line':self.LINE.strip(),
        'method':'POST',
        'path':'/path',
        'querystring':'query',
        }
        for key,value in things.items():
            self.assertEqual(value,getattr(self.rr,key))
            
class TestRequestParsesLineCRLF(RequestParsesLineTests,unittest.TestCase):
    def setUp(self):
        self.rr = Request(default_adj)
        newline='\r\n'
        (self.IE_CRAP,self.LINE,self.HEADERS,self.BODY,self.POST)=PARTS(newline)
        
class TestRequestParsesLineCR(RequestParsesLineTests,unittest.TestCase):
    def setUp(self):
        self.rr = Request(default_adj)
        newline='\r'
        (self.IE_CRAP,self.LINE,self.HEADERS,self.BODY,self.POST)=PARTS(newline)
        
class TestRequestParsesLineLF(RequestParsesLineTests,unittest.TestCase):
    def setUp(self):
        self.rr = Request(default_adj)
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
