#!/usr/bin/env python

import imp
import os
import sys
import unittest

from httpy.Config import ApplicationConfig
from httpy.Response import Response
from httpy.utils import uri_to_fs

from TestCaseHttpy import TestCaseHttpy
from utils import StubApplicationConfig

class TestUriToFs(TestCaseHttpy):

    def setUp(self):
        TestCaseHttpy.setUp(self)
        config = StubApplicationConfig()
        config.mode = 'development'
        config.verbosity = 0
        config.site_root = os.path.realpath(self.siteroot)
        config.app_uri_root = '/'
        config.app_fs_root = os.path.realpath(self.siteroot)
        config.__ = None
        self.config = config

    testsite = [ ('index.html', '')
               ,  '/__'
               ,  '/about'
               ,  '/My Documents'
               , ('/My Documents/index.html', '')
               ,  '/content'
               , ('/content/index.pt', '')
                ]


    def testBasic(self):
        expected = os.path.realpath(self.convert_path('root/index.html'))
        actual = uri_to_fs( self.config
                          , '/index.html'
                          , ()
                           )
        self.assertEqual(expected, actual)

    def testDefaultDocument(self):
        expected = os.path.realpath(self.convert_path('root/index.html'))
        actual = uri_to_fs( self.config
                          , '/'
                          , ('index.html',)
                           )
        self.assertEqual(expected, actual)

    def testNoDefaultRaisesForbidden(self):
        self.assertRaises( Response
                         , uri_to_fs
                         , self.config
                         , '/about/'
                         , ('index.html',)
                           )
        try:
            uri_to_fs(self.config, '/', ('index.html',))
        except Response, response:
            self.assertEqual(response.code, 403)

    def testNotThereRaisesNotFound(self):
        self.assertRaises( Response
                         , uri_to_fs
                         , self.config
                         , '/not-there'
                         , ()
                           )
        try:
            uri_to_fs(self.config, '/not-there', ('index.html',))
        except Response, response:
            self.assertEqual(response.code, 404)

    def testNoTrailingSlashIsRedirected(self):
        self.assertRaises( Response
                         , uri_to_fs
                         , self.config
                         , '/about'
                         , ()
                           )
        try:
            uri_to_fs(self.config, '/about', ())
        except Response, response:
            self.assertEqual(response.code, 301)
            self.assertEqual(response.headers['Location'], '/about/')

    def testEtcPasswdGoesUncaughtAtThisStage(self):
        # This test will of course fail if you have it buried deep on your fs.
        expected = self.convert_path('/etc/master.passwd')

        if not os.path.isfile(expected):
            # nevermind
            return

        actual = uri_to_fs( self.config
                          , '../../../../../../../../../../etc/master.passwd'
                          , ()
                           )
        self.assertEqual(expected, actual)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUriToFs))
    return suite

if __name__ == '__main__':
    unittest.main()
