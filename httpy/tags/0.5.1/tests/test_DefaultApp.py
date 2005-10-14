#!/usr/bin/env python

import imp
import os
import unittest

from httpy import DefaultApp
from httpy.Request import Request, ZopeRequest
from httpy.Response import Response

from TestCaseHttpy import TestCaseHttpy


class TestDefaultApp(TestCaseHttpy):

    def setUp(self):
        TestCaseHttpy.setUp(self)

        DefaultApp.Application.site_root = os.path.realpath(self.siteroot)
        DefaultApp.Application.fs_root = os.path.realpath(self.siteroot)
        DefaultApp.Application.uri_root = '/'

        self.app = DefaultApp.Application()

    testsite = [ ('/index.html', '')
               , ('/foo.bar', '')
               , ('/foo.png', '')
               , ('/foo.html', 'Greetings, program!')
                ]

    def testBasic(self):
        request = self.make_request("/")

        expected = Response(200)
        expected.headers['Last-Modified'] = 'blah blah blah'
        expected.headers['Content-Type'] = 'text/html'
        try:
            self.app.respond(request)
        except Response, actual:
            pass
        self.assertEqual(expected.code, actual.code)
        self.assertEqual(expected.headers.keys(), actual.headers.keys())
        self.assertEqual(expected.body, actual.body)


    # serve_static
    # ============

    def testUnknownFileTypeDefaultsToTextPlain(self):
        request = self.make_request("/foo.bar")
        expected = 'text/plain'
        try:
            self.app.respond(request)
        except Response, response:
            actual = response.headers['Content-Type']
        self.assertEqual(expected, actual)

    def testKnownFiletype(self):
        request = self.make_request("/foo.png")
        expected = 'image/png'
        try:
            self.app.respond(request)
        except Response, response:
            actual = response.headers['Content-Type']
        self.assertEqual(expected, actual)


    # 304
    # ===

    def testDevelopment_ModifiedSinceIsTrue(self):
        os.environ['HTTPY_MODE'] = 'development'
        self.app = DefaultApp.Application()

        headers = {'If-Modified-Since':'Fri, 01 Jan 1970 00:00:00 GMT'}
        request = self.make_request("/foo.html", headers)

        expected = Response(200)
        expected.headers['Last-Modified'] = 'blah blah blah'
        expected.headers['Content-Type'] = 'text/html'
        expected.body = 'Greetings, program!'
        try:
            self.app.respond(request)
        except Response, actual:
            pass
        self.assertEqual(expected.code, actual.code)
        self.assertEqual(expected.headers.keys(), actual.headers.keys())
        self.assertEqual(expected.body, actual.body)

    def testDevelopment_ModifiedSinceIsFalse(self):
        os.environ['HTTPY_MODE'] = 'development'
        self.app = DefaultApp.Application()

        headers = {'If-Modified-Since':'Fri, 31 Dec 9999 23:59:59 GMT'}
        request = self.make_request("/foo.html", headers)

        expected = Response(200)
        expected.headers['Last-Modified'] = 'blah blah blah'
        expected.headers['Content-Type'] = 'text/html'
        expected.body = 'Greetings, program!'
        try:
            self.app.respond(request)
        except Response, actual:
            pass
        self.assertEqual(expected.code, actual.code)
        self.assertEqual(expected.headers.keys(), actual.headers.keys())
        self.assertEqual(expected.body, actual.body)

    def testDeployment_ModifiedSinceIsTrue(self):
        os.environ['HTTPY_MODE'] = 'deployment'
        self.app = DefaultApp.Application()

        headers = {'If-Modified-Since':'Fri, 01 Jan 1970 00:00:00 GMT'}
        request = self.make_request("/foo.html", headers)

        expected = Response(200)
        expected.headers['Last-Modified'] = 'blah blah blah'
        expected.headers['Content-Type'] = 'text/html'
        expected.body = 'Greetings, program!'
        try:
            self.app.respond(request)
        except Response, actual:
            pass
        self.assertEqual(expected.code, actual.code)
        self.assertEqual(expected.headers.keys(), actual.headers.keys())
        self.assertEqual(expected.body, actual.body)

    def testDeployment_ModifiedSinceIsFalse(self):
        os.environ['HTTPY_MODE'] = 'deployment'
        self.app = DefaultApp.Application()

        headers = {'If-Modified-Since':'Fri, 31 Dec 9999 23:59:59 GMT'}
        request = self.make_request("/foo.html", headers)

        expected = Response(304)
        expected.headers['Last-Modified'] = 'blah blah blah'
        expected.headers['Content-Type'] = 'text/html'
        expected.body = '' # no body for 304
        try:
            self.app.respond(request)
        except Response, actual:
            pass
        self.assertEqual(expected.code, actual.code)
        self.assertEqual(expected.headers.keys(), actual.headers.keys())
        self.assertEqual(expected.body, actual.body)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDefaultApp))
    return suite

if __name__ == '__main__':
    unittest.main()
