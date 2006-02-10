#!/usr/bin/env python

import os
import unittest
from email.Message import Message

from httpy._zope.interface.exceptions import DoesNotImplement
from httpy._zope.server.adjustments import default_adj

from httpy import Request
from httpy.couplers.standalone.request import ZopeRequest


ZOPEREQ_API = [ '__doc__'
              , '__implemented__'
              , '__init__'
              , '__module__'
              , '__providedBy__'
              , '__provides__'
              , '_raw'
              , '_receiver'
              , '_tmp'
              , 'adj'
              , 'completed'
              , 'empty'
              , 'get_body'
              , 'get_headers'
              , 'get_line'
              , 'headers'
              , 'method'
              , 'parse_line'
              , 'path'
              , 'raw'
              , 'raw_body'
              , 'raw_headers'
              , 'raw_line'
              , 'received'
              , 'set_receiver'
              , 'uri'
               ]

REQUEST_API = [ '__doc__'
              , '__init__'
              , '__module__'
              , '__repr__'
              , '__str__'
              , 'headers'
              , 'method'
              , 'path'
              , 'raw'
              , 'raw_body'
              , 'raw_headers'
              , 'raw_line'
              , 'uri'
               ]


class TestRequest(unittest.TestCase):

    def setUp(self):
        self.zopereq = ZopeRequest(default_adj)
        self.zopereq.received("GET / HTTP/1.1\n\n")
        self.request = Request(self.zopereq)

    def testZopeRequestAPI(self):
        expected = ZOPEREQ_API
        actual = dir(self.zopereq)
        self.assertEqual(expected, actual)

    def testRequestAPI(self):
        expected = REQUEST_API
        actual = dir(self.request)
        self.assertEqual(expected, actual)

    def testNoBodyStillHasHeaders(self):
        expected = True
        actual = isinstance(self.request.headers, Message)
        self.assertEqual(expected, actual)

    def testBadRequestObject(self):
        self.assertRaises(DoesNotImplement, Request, object())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRequest))
    return suite

if __name__ == '__main__':
    unittest.main()
