#!/usr/bin/env python

import os
import stat
import unittest

from medusa import http_date

from httpy.Handler import Redirect
from httpy.Handler import RequestError
from HandlerTestCase import HandlerTestCase


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
    <p>Message: Found.</p>
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

dummy_error_500 = """\
<head>
    <title>Error response</title>
</head>
<body>
    <h1>Error response</h1>
    <p>Error code 500.</p>
    <p>Message: Internal Server Error.</p>
    """+"""
</body>"""

dummy_error_501 = """\
<head>
    <title>Error response</title>
</head>
<body>
    <h1>Error response</h1>
    <p>Error code 501.</p>
    <p>Message: Not Implemented.</p>
    """+"""
</body>"""


dummy_context_302 = """\
raise Redirect("http://www.example.com/")
"""

dummy_context_500 = """\
raise Exception("Whoa there!")
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

dummy_error_template = """\
<html>
  <head>
    <title>ERROR!!!!!!!</title>
  </head>
  <body>
    <table>
      <tr>
        <th>Resource</th>
        <td tal:content="request/uri"></td>
      </tr>
      <tr>
        <th>Error</th>
        <td tal:content="error/msg"></td>
      </tr>
      <tr>
        <th>Code</th>
        <td tal:content="error/code"></td>
      </tr>
      <tr tal:condition="message">
        <th>Message</th>
        <td tal:content="error/message"></td>
      </tr>
    </table>
  </body>
</html>"""

dummy_error_template_expanded = """\
<html>
  <head>
    <title>ERROR!!!!!!!</title>
  </head>
  <body>
    <table>
      <tr>
        <th>Resource</th>
        <td>/not-there</td>
      </tr>
      <tr>
        <th>Error</th>
        <td>Not Found</td>
      </tr>
      <tr>
        <th>Code</th>
        <td>404</td>
      </tr>
      """+"""
    </table>
  </body>
</html>"""


dummy_last_resort = """\
<head>
    <title>Error response</title>
</head>
<body>
    <h1>Error response</h1>
    <p>Error code 500.</p>
    <p>Message: There was a dire error serving your request.</p>
</body>"""



class TestGetError(HandlerTestCase):

    def buildTestSite(self):
        os.mkdir('root')
        file('root/index.html', 'w')
        os.mkdir('root/about')
        os.mkdir('root/__')
        file('root/foo.pt', 'w')

    def test301(self):
        self.request.uri = '/about'
        try:
            self.handler._setpath(self.request)
        except Redirect, error:
            pass
        expected = dummy_error_301
        actual = self.handler._geterror(self.request, error)
        self.assertEqual(expected, actual)
        self.assertEqual(self.request['Content-Length'], 216L)
        self.assertEqual(self.request['Content-Type'], 'text/html')
        self.assertEqual(self.request.reply_code, 301)

    def test302(self):
        file_ = open('root/__/context.py', 'w')
        file_.write(dummy_context_302)
        file_.close()
        self.handler._setpath(self.request)
        try:
            self.handler._gettemplate(self.request)
        except Redirect, error:
            pass
        expected = dummy_error_302
        actual = self.handler._geterror(self.request, error)
        self.assertEqual(expected, actual)
        self.assertEqual(self.request['Content-Length'], 236L)
        self.assertEqual(self.request['Content-Type'], 'text/html')
        self.assertEqual(self.request.reply_code, 302)

    def test304(self):
        self.request.uri = '/index.html'
        self.handler._setpath(self.request)
        self.handler.mode = 'deployment'
        mtime = os.stat(self.request.path)[stat.ST_MTIME]
        ims = 'If-Modified-Since: %s' % http_date.build_http_date(mtime)
        self.request.header.insert(len(self.request.header), ims)
        try:
            self.handler._getstatic(self.request)
        except RequestError, error:
            pass
        expected = dummy_error_304
        actual = self.handler._geterror(self.request, error)
        self.assertEqual(expected, actual)
        self.assertEqual(self.request.reply_code, 304)

    def test400(self):
        self.request.uri = '../../../../../../../etc/master.passwd'
        try:
            self.handler._setpath(self.request)
        except RequestError, error:
            pass
        expected = dummy_error_400
        actual = self.handler._geterror(self.request, error)
        self.assertEqual(expected, actual)
        self.assertEqual(self.request['Content-Length'], 156L)
        self.assertEqual(self.request['Content-Type'], 'text/html')
        self.assertEqual(self.request.reply_code, 400)

    def test403(self):
        self.request.uri = '/about/'
        try:
            self.handler._setpath(self.request)
        except RequestError, error:
            pass
        expected = dummy_error_403
        actual = self.handler._geterror(self.request, error)
        self.assertEqual(expected, actual)
        self.assertEqual(self.request['Content-Length'], 154L)
        self.assertEqual(self.request['Content-Type'], 'text/html')
        self.assertEqual(self.request.reply_code, 403)

    def test404(self):
        self.request.uri = '/not-there'
        try:
            self.handler._setpath(self.request)
        except RequestError, error:
            pass
        expected = dummy_error_404
        actual = self.handler._geterror(self.request, error)
        self.assertEqual(expected, actual)
        self.assertEqual(self.request['Content-Length'], 154L)
        self.assertEqual(self.request['Content-Type'], 'text/html')
        self.assertEqual(self.request.reply_code, 404)

    def test500(self):
        self.request.uri = '/foo.pt'
        self.handler._setpath(self.request)
        file_ = open('root/__/context.py', 'w')
        file_.write(dummy_context_500)
        file_.close()
        try:
            self.handler._handle_request_unsafely(self.request)
        except RequestError, error:
            pass
        expected = dummy_error_500
        actual = self.handler._geterror(self.request, error)
        self.assertEqual(expected, actual)
        self.assertEqual(self.request['Content-Length'], 166L)
        self.assertEqual(self.request['Content-Type'], 'text/html')
        self.assertEqual(self.request.reply_code, 500)

    def test501(self):
        self.request.command = 'POST' # :-(
        try:
            self.handler._handle_request_unsafely(self.request)
        except RequestError, error:
            pass
        expected = dummy_error_501
        actual = self.handler._geterror(self.request, error)
        self.assertEqual(expected, actual)
        self.assertEqual(self.request['Content-Length'], 160L)
        self.assertEqual(self.request['Content-Type'], 'text/html')
        self.assertEqual(self.request.reply_code, 501)

    def testErrorTemplate(self):
        file_ = open('root/__/error.pt', 'w')
        file_.write(dummy_error_template)
        file_.close()
        self.request.uri = '/not-there'
        try:
            self.handler._setpath(self.request)
        except RequestError, error:
            pass
        expected = dummy_error_template_expanded
        actual = self.handler._geterror(self.request, error)
        self.assertEqual(expected, actual)
        self.assertEqual(self.request['Content-Length'], 332L)
        self.assertEqual(self.request['Content-Type'], 'text/html')
        self.assertEqual(self.request.reply_code, 404)

    def testEmptyErrorTemplateIgnored(self):
        file('root/__/error.pt', 'w') # empty file
        self.request.uri = '/not-there'
        try:
            self.handler._setpath(self.request)
        except RequestError, error:
            pass
        expected = dummy_error_404
        actual = self.handler._geterror(self.request, error)
        self.assertEqual(expected, actual)
        self.assertEqual(self.request['Content-Length'], 154L)
        self.assertEqual(self.request['Content-Type'], 'text/html')
        self.assertEqual(self.request.reply_code, 404)

    def testLastResort(self):
        def bad_geterror(request, error):
            raise Exception("Muahahahaha!!!!")
        self.handler._geterror = bad_geterror
        self.request.uri = '/not-there'
        try:
            self.handler._setpath(self.request)
        except Exception, error:
            pass
        expected = dummy_last_resort
        actual = self.handler._handle_request_safely(self.request)
        self.assertEqual(expected, actual)
        self.assertEqual(self.request['Content-Length'], 183L)
        self.assertEqual(self.request['Content-Type'], 'text/html')
        self.assertEqual(self.request.reply_code, 500)




def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGetError))
    return suite

if __name__ == '__main__':
    unittest.main()
