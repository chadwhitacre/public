#!/usr/bin/env python

# Make sure we can find the module we want to test.
# =================================================

import os
import sys
if __name__ == '__main__':
    sys.path.insert(0, os.path.realpath('..'))


# Import some modules.
# ====================

import httpy
import unittest
from medusa import http_server
from httpyTestCase import httpyTestCase
from simpletal import simpleTAL


# Define the site to test against.
# ================================

dummy_html = """\
<html>
  <head>
    <title>Foo</title>
  </head>
  <body>
    Bar
  </body>
</html>"""

def buildTestSite():
    os.mkdir('root')
    file_ = open('root/index.html','w')
    file_.write(dummy_html)
    file_.close()
    file('root/empty', 'w')


# Define our testing class.
# =========================

class TestGetStatic(httpyTestCase):

    def setUp(self):

        # [re]build a temporary website tree in ./root
        self.removeTestSite()
        buildTestSite()

        # handler
        self.request = http_server.http_request(*self._request)
        handler_config = httpy.parse_config('')[1]
        self.handler = httpy.Handler(**handler_config)
        self.handler.setpath(self.request)

    def testBasic(self):
        expected = dummy_html
        actual = self.handler.getstatic(self.request)
        self.assertEqual(expected, actual)
        self.assertEqual(self.request['Content-Length'], 83L)
        self.assertEqual(self.request['Content-Type'], 'text/html')

    def testEmptyFile(self):
        self.request.uri = '/empty'
        self.handler.setpath(self.request)
        expected = ''
        actual = self.handler.getstatic(self.request)
        self.assertEqual(expected, actual)
        self.assertEqual(self.request['Content-Length'], 0)
        self.assertEqual(self.request['Content-Type'], 'text/plain')

    def tearDown(self):
        self.removeTestSite()
        pass



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGetStatic))
    return suite

if __name__ == '__main__':
    unittest.main()
