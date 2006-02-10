#!/usr/bin/env python

import os
import unittest

from httpy._zope.server.adjustments import default_adj

from httpy.couplers.standalone.request import ZopeRequest

from utils import REQUEST_PARTS

def TE_HEADERS(newline):
    return newline.join([
          "Host: josemaria:5370"
        , "User-Agent: Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.10) Gecko/20050716 Firefox/1.0.6"
        , "Accept: text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5"
        , "Accept-Language: en-us,en;q=0.7,ar;q=0.3"
        , "Accept-Encoding: gzip,deflate"
        , "Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7"
        , "Keep-Alive: 300"
        , "Connection: keep-alive"
        , "Referer: http://www.zetadev.com/tmp/test.html"
        , "Content-Type: application/x-www-form-urlencoded"
        , "Content-Length: %s"
        , "Transfer-Encoding:%s"
        , newline
         ])

from httpy._zope.server.fixedstreamreceiver import FixedStreamReceiver
from httpy._zope.server.http.chunking import ChunkedReceiver
from httpy._zope.server.buffers import OverflowableBuffer

class RequestSetReceiversTests:

    def testNoLengthNoEncoding(self):
        length=0
        encoding=''
        self.request.received(self.LINE+self.TE_HEADERS%(length,encoding)+' ')
        self.assertEqual(self.request._receiver,None)
        self.assert_(self.request.completed)
        self.assertEqual(self.request.raw_body,'')

    def testNoLengthEncoding(self):
        length=0
        encoding='chunked'
        self.request.received(self.LINE+self.TE_HEADERS%(length,encoding)+' ')
        self.assert_(isinstance(self.request._receiver,ChunkedReceiver))

    def testLengthNoEncoding(self):
        length=8
        encoding=''
        self.request.received(self.LINE+self.TE_HEADERS%(length,encoding)+' ')
        self.assert_(isinstance(self.request._receiver,FixedStreamReceiver))

    def testLengthEncoding(self):
        length=8
        encoding='chunked'
        self.request.received(self.LINE+self.TE_HEADERS%(length,encoding)+' ')
        self.assert_(isinstance(self.request._receiver,ChunkedReceiver))


class TestRequestSetReceiversCRLF(RequestSetReceiversTests,unittest.TestCase):
    def setUp(self):
        self.request = ZopeRequest(default_adj)
        self.newline='\r\n'
        (self.IE_CRAP,self.LINE,self.LINE2,self.HEADERS,self.HEADERS2,self.BODY,self.POST,self.GET)=REQUEST_PARTS(self.newline)
        self.TE_HEADERS = TE_HEADERS(self.newline)

class TestRequestGetsHeadersCR(RequestSetReceiversTests,unittest.TestCase):
    def setUp(self):
        self.request = ZopeRequest(default_adj)
        self.newline='\r'
        (self.IE_CRAP,self.LINE,self.LINE2,self.HEADERS,self.HEADERS2,self.BODY,self.POST,self.GET)=REQUEST_PARTS(self.newline)
        self.TE_HEADERS = TE_HEADERS(self.newline)

class TestRequestGetsHeadersLF(RequestSetReceiversTests,unittest.TestCase):
    def setUp(self):
        self.request = ZopeRequest(default_adj)
        self.newline='\n'
        (self.IE_CRAP,self.LINE,self.LINE2,self.HEADERS,self.HEADERS2,self.BODY,self.POST,self.GET)=REQUEST_PARTS(self.newline)
        self.TE_HEADERS = TE_HEADERS(self.newline)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRequestSetReceiversCRLF))
    suite.addTest(makeSuite(TestRequestGetsHeadersCR))
    suite.addTest(makeSuite(TestRequestGetsHeadersLF))
    return suite

if __name__ == '__main__':
    unittest.main()
