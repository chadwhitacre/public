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
          , '/'
          , '1.1'
          , ['Host: josemaria:8080', 'User-Agent: Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.10) Gecko/20050716 Firefox/1.0.6', 'Accept: text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5', 'Accept-Language: en-us,en;q=0.7,ar;q=0.3', 'Accept-Encoding: gzip,deflate', 'Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Keep-Alive: 300', 'Connection: keep-alive']
           )
handler_config = httpy.parse_config('')[1]


# Define the site to test against.
# ================================

def buildTestSite():
    os.mkdir('root')
    os.mkdir('root/__')
    frame = file('root/__/frame.pt','w')
    frame.write("""\
<html>
    foo
</html>
""")
    frame.close()


# Define our testing class.
# =========================

class TestFrame(httpyTestCase):

    def setUp(self):

        # [re]build a temporary website tree in ./root
        self.removeTestSite()
        buildTestSite()

        # handler
        self.request = http_server.http_request(*request)
        self.handler = httpy.handler(**handler_config)

    def testHasFrame(self):
        file_ = open('root/__/frame.pt','r')
        expected = simpleTAL.compileXMLTemplate(file_)
        actual = self.handler.getframe()
        self.assertEqual(type(expected), type(actual))
        self.assertEqual(str(expected), str(actual))

    def testNoFrame(self):
        os.remove('root/__/frame.pt')
        expected = None
        actual = self.handler.getframe()
        self.assertEqual(expected, actual)

    def tearDown(self):
        self.removeTestSite()
        pass



if __name__ == '__main__':
    unittest.main()
