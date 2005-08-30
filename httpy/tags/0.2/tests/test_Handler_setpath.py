#!/usr/bin/env python

import os
import unittest

from medusa import http_server

from httpy.Handler import Handler
from httpy.Handler import RequestError
from httpy.Handler import Redirect
from httpy.Configuration import Configuration
from HandlerTestCase import HandlerTestCase


class TestSetPath(HandlerTestCase):

    setpath = False

    def buildTestSite(self):
        os.mkdir('root')
        file('root/index.html', 'w')
        os.mkdir('root/__')
        file('root/__/frame.pt', 'w')
        os.mkdir('root/about')
        os.mkdir('root/My Documents')
        file('root/My Documents/index.html', 'w')
        os.mkdir('root/content')
        file('root/content/index.pt', 'w')

    def testRootIsSetAsExpected(self):
        self.assertEqual(self.handler.root, os.path.realpath('./root'))

    def testBasic(self):
        self.request.uri = '/index.html'
        self.handler._setpath(self.request)
        expected = os.path.realpath('root/index.html')
        actual = self.request.path
        self.assertEqual(expected, actual)

    def testStaticDefaultDocument(self):
        self.request.uri = '/'
        self.handler._setpath(self.request)
        expected = os.path.realpath('root/index.html')
        actual = self.request.path
        self.assertEqual(expected, actual)

    def testTemplateDefaultDocument(self):
        self.request.uri = '/content/'
        self.handler._setpath(self.request)
        expected = os.path.realpath('root/content/index.pt')
        actual = self.request.path
        self.assertEqual(expected, actual)

    def testEncodedURIGetsUnencoded(self):
        self.request.uri = '/My%20Documents/'
        self.handler._setpath(self.request)
        expected = os.path.realpath( 'root/My Documents/index.html')
        actual = self.request.path
        self.assertEqual(expected, actual)

    def testDoubleRootRaisesBadRequest(self):
        self.request.uri = '//index.html'
        self.assertRaises( RequestError
                         , self.handler._setpath
                         , self.request
                          )
        try:
            self.handler._setpath(self.request)
        except RequestError, err:
            self.assertEqual(err.code, 400)

    def testNoDefaultRaisesForbidden(self):
        self.request.uri = '/about/'
        self.assertRaises( RequestError
                         , self.handler._setpath
                        , self.request
                          )
        try:
            self.handler._setpath(self.request)
        except RequestError, err:
            self.assertEqual(err.code, 403)

    def testNotThereRaisesNotFound(self):
        self.request.uri = '/not-there'
        self.assertRaises( RequestError
                         , self.handler._setpath
                         , self.request
                          )
        try:
            self.handler._setpath(self.request)
        except RequestError, err:
            self.assertEqual(err.code, 404)

    def testOutsideRootRaisesBadRequest(self):
        self.request.uri = '/../../../../../../../etc/master.passwd'
        self.assertRaises( RequestError
                         , self.handler._setpath
                         , self.request
                          )
        try:
            self.handler._setpath(self.request)
        except RequestError, err:
            self.assertEqual(err.code, 400)

    def testMagicDirectoryReturnsNotFound(self):
        self.request.uri = '/__/frame.pt'
        self.assertRaises( RequestError
                         , self.handler._setpath
                         , self.request
                          )
        try:
            self.handler._setpath(self.request)
        except RequestError, err:
            self.assertEqual(err.code, 404)

    def testNoMagicDirectoryDoesntReturnNotFound(self):
        os.remove('root/__/frame.pt')
        os.rmdir('root/__')
        config = Configuration(['-rroot'])
        self.handler = Handler(**config.handler)
        self.handler._setpath(self.request)
        expected = os.path.realpath('root/index.html')
        actual = self.request.path
        self.assertEqual(expected, actual)

    def testNoTrailingSlashIsRedirected(self):
        self.request.uri = '/about'
        self.assertRaises( Redirect
                         , self.handler._setpath
                         , self.request
                          )
        try:
            self.handler._setpath(self.request)
        except Redirect, err:
            self.assertEqual(err.code, 301)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSetPath))
    return suite

if __name__ == '__main__':
    unittest.main()
