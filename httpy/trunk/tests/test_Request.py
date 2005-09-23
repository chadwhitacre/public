#!/usr/bin/env python

import os
import unittest

from zope.server.adjustments import default_adj

from httpy.Request import ZopeRequest


class TestRequest(unittest.TestCase):
    """These tests cover overall instantiation of a Request.



    """

    def setUp(self):
        self.request = ZopeRequest(default_adj)


    def testPostWithBody(self):
        req = ("POST / HTTP/1.1\r\ncontent-length: 7\r\n\r\nfoo=bar\r\n")
        self.request.received(req)
        self.assert_(self.request.completed)

    def testGetWithNoBody(self):
        req = "GET / HTTP/1.1\r\nHost: josemaria:5370\r\n\r\n"
        self.request.received(req)
        self.assert_(self.request.completed)

    def testGetWithNoHeadersEither(self):
        req = "GET / HTTP/1.1\r\n\r\n"
        self.request.received(req)
        self.assert_(self.request.completed)





def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRequest))
    return suite

if __name__ == '__main__':
    unittest.main()
