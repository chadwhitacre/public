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
import stat
import unittest
from httpy import RequestProblem
from medusa import http_server, http_date
from httpyTestCase import httpyTestCase
from simpletal import simpleTAL
from xml.sax import SAXParseException


# Define the site to test against.
# ================================

dummy_error_301 = """\
<head>
    <title>Error response</title>
</head>
<body>
    <h1>Error response</h1>
    <p>Error code 301.</p>
    <p>Message: Moved Permanently.</p>
    Resource now resides at <a href="/about/">/about/</a>."""+"""
</body>"""

dummy_error_302 = """\
<head>
    <title>Error response</title>
</head>
<body>
    <h1>Error response</h1>
    <p>Error code 302.</p>
    <p>Message: Moved Temporarily.</p>
    Resource now resides at <a href="http://www.example.com/">http://www.example.com/</a>."""+"""
</body>"""

dummy_error_304 = ""

dummy_error_400 = """\
<head>
    <title>Error response</title>
</head>
<body>
    <h1>Error response</h1>
    <p>Error code 400.</p>
    <p>Message: Bad Request.</p>
    """+"""
</body>"""

dummy_error_403 = """\
<head>
    <title>Error response</title>
</head>
<body>
    <h1>Error response</h1>
    <p>Error code 403.</p>
    <p>Message: Forbidden.</p>
    """+"""
</body>"""

dummy_error_404 = """\
<head>
    <title>Error response</title>
</head>
<body>
    <h1>Error response</h1>
    <p>Error code 404.</p>
    <p>Message: Not Found.</p>
    """+"""
</body>"""



dummy_context = """\
raise RequestProblem(302, new_location="http://www.example.com/")
"""

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
    file('root/index.html', 'w')
    os.mkdir('root/about')
    os.mkdir('root/__')
    file_ = open('root/__/context.py', 'w')
    file_.write(dummy_context)
    file_.close()
    file_ = open('root/foo.pt', 'w')
    file_.write(dummy_tal)
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

    def test301(self):
        self.request.uri = '/about'
        try:
            self.handler.setpath(self.request)
        except RequestProblem, problem:
            pass
        expected = dummy_error_301
        actual = self.handler.getproblem(self.request, problem)
        self.assertEqual(expected, actual)
        self.assertEqual(self.request['Content-Length'], 216L)
        self.assertEqual(self.request['Content-Type'], 'text/html')

    def test302(self):
        self.handler.setpath(self.request)
        try:
            self.handler.gettemplate(self.request)
        except RequestProblem, problem:
            pass
        expected = dummy_error_302
        actual = self.handler.getproblem(self.request, problem)
        self.assertEqual(expected, actual)
        self.assertEqual(self.request['Content-Length'], 248L)
        self.assertEqual(self.request['Content-Type'], 'text/html')

    def test304(self):
        self.request.uri = '/index.html'
        self.handler.setpath(self.request)
        self.handler.dev_mode = False
        mtime = os.stat(self.request.path)[stat.ST_MTIME]
        ims = 'If-Modified-Since: %s' % http_date.build_http_date(mtime)
        self.request.header.insert(len(self.request.header), ims)
        try:
            self.handler.getstatic(self.request)
        except RequestProblem, problem:
            pass
        expected = dummy_error_304
        actual = self.handler.getproblem(self.request, problem)
        self.assertEqual(expected, actual)

    def test400(self):
        self.request.uri = '../../../../../../../etc/master.passwd'
        try:
            self.handler.setpath(self.request)
        except RequestProblem, problem:
            pass
        expected = dummy_error_400
        actual = self.handler.getproblem(self.request, problem)
        self.assertEqual(expected, actual)
        self.assertEqual(self.request['Content-Length'], 156L)
        self.assertEqual(self.request['Content-Type'], 'text/html')

    def test403(self):
        self.request.uri = '/about/'
        try:
            self.handler.setpath(self.request)
        except RequestProblem, problem:
            pass
        expected = dummy_error_403
        actual = self.handler.getproblem(self.request, problem)
        self.assertEqual(expected, actual)
        self.assertEqual(self.request['Content-Length'], 154L)
        self.assertEqual(self.request['Content-Type'], 'text/html')

    def test404(self):
        self.request.uri = '/not-there'
        try:
            self.handler.setpath(self.request)
        except RequestProblem, problem:
            pass
        expected = dummy_error_404
        actual = self.handler.getproblem(self.request, problem)
        self.assertEqual(expected, actual)
        self.assertEqual(self.request['Content-Length'], 154L)
        self.assertEqual(self.request['Content-Type'], 'text/html')

    def testErrorTemplate(self):
        pass

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