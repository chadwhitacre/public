#!/usr/bin/env python

import os
import unittest

from zope.server.adjustments import default_adj

from httpy.Request import ZopeRequest

from utils import REQUEST_PARTS


class RequestReceivedTests:

    def testSetsCompleted(self):
        self.request.received(self.POST)
        self.assert_(self.request.completed)

    def testDoesntSetCompleted(self):
        self.request.received(self.POST[:-1])
        self.assert_(not self.request.completed)

    def testReturnsBlockSize(self):
        size = self.request.received(self.POST)
        self.assertEqual(size, len(self.POST))


class TestRequestReceivedCRLF(RequestReceivedTests,unittest.TestCase):
    def setUp(self):
        self.request = ZopeRequest(default_adj)
        newline='\r\n'
        (self.IE_CRAP,self.LINE,self.LINE2,self.HEADERS,self.HEADERS2,self.BODY,self.POST,self.GET)=REQUEST_PARTS(newline)

class TestRequestReceivedCR(RequestReceivedTests,unittest.TestCase):
    def setUp(self):
        self.request = ZopeRequest(default_adj)
        newline='\r'
        (self.IE_CRAP,self.LINE,self.LINE2,self.HEADERS,self.HEADERS2,self.BODY,self.POST,self.GET)=REQUEST_PARTS(newline)

class TestRequestReceivedLF(RequestReceivedTests,unittest.TestCase):
    def setUp(self):
        self.request = ZopeRequest(default_adj)
        newline='\n'
        (self.IE_CRAP,self.LINE,self.LINE2,self.HEADERS,self.HEADERS2,self.BODY,self.POST,self.GET)=REQUEST_PARTS(newline)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRequestReceivedCRLF))
    suite.addTest(makeSuite(TestRequestReceivedCR))
    suite.addTest(makeSuite(TestRequestReceivedLF))
    return suite

if __name__ == '__main__':
    unittest.main()
