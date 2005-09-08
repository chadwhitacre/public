#!/usr/bin/env python

import os
import unittest

from HandlerTestCase import HandlerTestCase


dummy_html = """\
<html>
  <head>
    <title>Foo</title>
  </head>
  <body>
    Bar
  </body>
</html>"""


class TestGetStatic(HandlerTestCase):

    def buildTestSite(self):
        os.mkdir('root')
        file_ = open('root/index.html','w')
        file_.write(dummy_html)
        file_.close()
        file('root/empty', 'w')

    def setUp2(self):
        self.handler._setpath(self.request)

    def testBasic(self):
        expected = dummy_html
        actual = self.handler._getstatic(self.request)
        self.assertEqual(expected, actual)
        self.assertEqual(self.request['Content-Length'], 83L)
        self.assertEqual(self.request['Content-Type'], 'text/html')

    def testEmptyFile(self):
        self.request.uri = '/empty'
        self.handler._setpath(self.request)
        expected = ''
        actual = self.handler._getstatic(self.request)
        self.assertEqual(expected, actual)
        self.assertEqual(self.request['Content-Length'], 0)
        self.assertEqual(self.request['Content-Type'], 'text/plain')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGetStatic))
    return suite

if __name__ == '__main__':
    unittest.main()
