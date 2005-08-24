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


# Define the site to test against.
# ================================

def buildTestSite():
    os.mkdir('root')
    file('root/index.html', 'w')
    os.mkdir('root/__')
    file('root/__/frame.pt', 'w')
    os.mkdir('root/about')
    os.mkdir('root/My Documents')
    file('root/My Documents/index.html', 'w')
    os.mkdir('root/content')
    file('root/content/index.pt', 'w')


# Define our testing class.
# =========================

class TestSetPath(httpyTestCase):

    def setUp(self):

        # [re]build a temporary website tree in ./root
        self.removeTestSite()
        buildTestSite()

        # handler
        self.request = http_server.http_request(*self._request)
        handler_config = httpy.parse_config('')[1]
        self.handler = httpy.handler(**handler_config)

    def testRootIsSetAsExpected(self):
        self.assertEqual(self.handler.root, os.path.realpath('./root'))

    def testBasic(self):
        self.request.uri = '/index.html'
        self.handler.setpath(self.request)
        expected = os.path.realpath('root/index.html')
        actual = self.request.path
        self.assertEqual(expected, actual)

    def testStaticDefaultDocument(self):
        self.request.uri = '/'
        self.handler.setpath(self.request)
        expected = os.path.realpath('root/index.html')
        actual = self.request.path
        self.assertEqual(expected, actual)

    def testTemplateDefaultDocument(self):
        self.request.uri = '/content/'
        self.handler.setpath(self.request)
        expected = os.path.realpath('root/content/index.pt')
        actual = self.request.path
        self.assertEqual(expected, actual)

    def testEncodedURIGetsUnencoded(self):
        self.request.uri = '/My%20Documents/'
        self.handler.setpath(self.request)
        expected = os.path.realpath( 'root/My Documents/index.html')
        actual = self.request.path
        self.assertEqual(expected, actual)

    def testDoubleRootRaisesBadRequest(self):
        self.request.uri = '//index.html'
        self.assertRaises( httpy.RequestProblem
                         , self.handler.setpath
                         , self.request
                          )
        try:
            self.handler.setpath(self.request)
        except httpy.RequestProblem, err:
            self.assertEqual(err.code, 400)

    def testNoDefaultRaisesForbidden(self):
        self.request.uri = '/about/'
        self.assertRaises( httpy.RequestProblem
                         , self.handler.setpath
                        , self.request
                          )
        try:
            self.handler.setpath(self.request)
        except httpy.RequestProblem, err:
            self.assertEqual(err.code, 403)

    def testNotThereRaisesNotFound(self):
        self.request.uri = '/not-there'
        self.assertRaises( httpy.RequestProblem
                         , self.handler.setpath
                         , self.request
                          )
        try:
            self.handler.setpath(self.request)
        except httpy.RequestProblem, err:
            self.assertEqual(err.code, 404)

    def testOutsideRootRaisesBadRequest(self):
        self.request.uri = '/../../../../../../../etc/master.passwd'
        self.assertRaises( httpy.RequestProblem
                         , self.handler.setpath
                         , self.request
                          )
        try:
            self.handler.setpath(self.request)
        except httpy.RequestProblem, err:
            self.assertEqual(err.code, 400)

    def testMagicDirectoryReturnsNotFound(self):
        self.request.uri = '/__/frame.pt'
        self.assertRaises( httpy.RequestProblem
                         , self.handler.setpath
                         , self.request
                          )
        try:
            self.handler.setpath(self.request)
        except httpy.RequestProblem, err:
            self.assertEqual(err.code, 404)

    def testNoMagicDirectoryDoesntReturnNotFound(self):
        os.remove('root/__/frame.pt')
        os.rmdir('root/__')
        handler_config = httpy.parse_config('')[1]
        self.handler = httpy.handler(**handler_config)
        self.handler.setpath(self.request)
        expected = os.path.realpath('root/index.html')
        actual = self.request.path
        self.assertEqual(expected, actual)

    def testNoTrailingSlashIsRedirected(self):
        self.request.uri = '/about'
        self.assertRaises( httpy.RequestProblem
                         , self.handler.setpath
                         , self.request
                          )
        try:
            self.handler.setpath(self.request)
        except httpy.RequestProblem, err:
            self.assertEqual(err.code, 301)

    def tearDown(self):
        self.removeTestSite()



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSetPath))
    return suite

if __name__ == '__main__':
    unittest.main()
