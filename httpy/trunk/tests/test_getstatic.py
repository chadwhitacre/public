#!/usr/bin/env python

# Make sure we can find the module we want to test.
# =================================================

import os
import sys
sys.path.insert(0, os.path.realpath('..'))


# Import some modules.
# ====================

import httpy
import unittest
from medusa import http_server
from httpyTestCase import httpyTestCase
from simpletal import simpleTAL


# Set up some a dummy request and handler.
# ========================================

request = ( None
          , 'GET / HTTP/1.1'
          , 'GET'
          , '/index.html'
          , '1.1'
          , ['Host: josemaria:8080', 'User-Agent: Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.10) Gecko/20050716 Firefox/1.0.6', 'Accept: text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5', 'Accept-Language: en-us,en;q=0.7,ar;q=0.3', 'Accept-Encoding: gzip,deflate', 'Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Keep-Alive: 300', 'Connection: keep-alive']
           )
handler_config = httpy.parse_config('')[1]


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
</html>
"""

def buildTestSite():
    os.mkdir('root')
    file_ = open('root/index.html','w')
    file_.write(dummy_html)
    file_.close()
    file('root/empty', 'w')


# Define our testing class.
# =========================

class TestHandleStatic(httpyTestCase):

    def setUp(self):

        # [re]build a temporary website tree in ./root
        self.removeTestSite()
        buildTestSite()

        # handler
        self.request = http_server.http_request(*request)
        self.handler = httpy.handler(**handler_config)
        self.handler.setpath(self.request)

    def testBasic(self):
        expected = dummy_html
        actual = self.handler.getstatic(self.request)
        self.assertEqual(expected, actual)
        self.assertEqual(self.request['Content-Length'], 84L)
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



if __name__ == '__main__':
    unittest.main()
