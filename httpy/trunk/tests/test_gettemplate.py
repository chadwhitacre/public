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
from xml.sax import SAXParseException


# Define the site to test against.
# ================================

dummy_tal = """\
<html>
  <head>
    <title>Foo</title>
  </head>
  <body>
    Bar
  </body>
</html>"""

dummy_frame = """\
<html metal:define-macro="frame">
  <head>
    <title>Foo</title>
  </head>
  <body metal:define-slot="body">
    Bar
  </body>
</html>"""

dummy_metal = """\
<html metal:use-macro="frame">
  <body metal:fill-slot="body">
    Baz
  </body>
</html>"""

dummy_expanded = """\
<html>
  <head>
    <title>Foo</title>
  </head>
  <body>
    Baz
  </body>
</html>"""


def buildTestSite():
    os.mkdir('root')
    file_ = open('root/index.pt','w')
    file_.write(dummy_tal)
    file_.close()
    file('root/empty', 'w')
    os.mkdir('root/__')
    file_ = open('root/__/frame.pt','w')
    file_.write(dummy_frame)
    file_.close()
    file_ = open('root/framed.pt','w')
    file_.write(dummy_metal)
    file_.close()



# Define our testing class.
# =========================

class TestGetTemplate(httpyTestCase):

    def setUp(self):

        # [re]build a temporary website tree in ./root
        self.removeTestSite()
        buildTestSite()

        # handler
        self.request = http_server.http_request(*self._request)
        handler_config = httpy.parse_config('')[1]
        self.handler = httpy.handler(**handler_config)
        self.handler.setpath(self.request)

    def testBasic(self):
        expected = dummy_tal
        actual = self.handler.gettemplate(self.request)
        self.assertEqual(expected, actual)
        self.assertEqual(self.request['Content-Length'], 83L)
        self.assertEqual(self.request['Content-Type'], 'text/html')

    def testEmptyFile(self):
        self.request.uri = '/empty'
        self.handler.setpath(self.request)
        self.assertRaises( SAXParseException
                         , self.handler.gettemplate
                         , self.request
                          )

    def testTemplateUsingFrame(self):
        self.request.uri = '/framed.pt'
        self.handler.setpath(self.request)
        expected = dummy_expanded
        actual = self.handler.gettemplate(self.request)
        self.assertEqual(expected, actual)
        self.assertEqual(self.request['Content-Length'], 83L)
        self.assertEqual(self.request['Content-Type'], 'text/html')

    def tearDown(self):
        self.removeTestSite()
        pass



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGetTemplate))
    return suite

if __name__ == '__main__':
    unittest.main()
