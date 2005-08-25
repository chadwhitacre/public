#!/usr/bin/env python

import os
import unittest
from xml.sax import SAXParseException

from httpy.Handler import Handler
from HandlerTestCase import HandlerTestCase


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


class TestGetTemplate(HandlerTestCase):

    def buildTestSite(self):
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

    def testBasic(self):
        expected = dummy_tal
        actual = self.handler._gettemplate(self.request)
        self.assertEqual(expected, actual)
        self.assertEqual(self.request['Content-Length'], 83L)
        self.assertEqual(self.request['Content-Type'], 'text/html')

    def testEmptyFile(self):
        self.request.uri = '/empty'
        self.handler._setpath(self.request)
        self.assertRaises( SAXParseException
                         , self.handler._gettemplate
                         , self.request
                          )

    def testTemplateUsingFrame(self):
        self.request.uri = '/framed.pt'
        self.handler._setpath(self.request)
        expected = dummy_expanded
        actual = self.handler._gettemplate(self.request)
        self.assertEqual(expected, actual)
        self.assertEqual(self.request['Content-Length'], 83L)
        self.assertEqual(self.request['Content-Type'], 'text/html')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGetTemplate))
    return suite

if __name__ == '__main__':
    unittest.main()
