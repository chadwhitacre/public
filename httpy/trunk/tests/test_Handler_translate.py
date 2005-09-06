#!/usr/bin/env python

import os
import unittest

from HandlerTestCase import HandlerTestCase


DUMMY_REQUEST = [
    'HTTP/1.1 GET /'
  , ''
   ]
DUMMY_REQUEST = '\r\n'.join(DUMMY_REQUEST)


class TestTranslate(HandlerTestCase):

    def buildTestSite(self):
        pass

    def testBasic(self):
        response = self.send('GET / HTTP/1.1\r\n\r\n')
        print response


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTranslate))
    return suite

if __name__ == '__main__':
    unittest.main()
