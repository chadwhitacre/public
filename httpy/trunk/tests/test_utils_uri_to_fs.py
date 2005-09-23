#!/usr/bin/env python

import imp
import os
import unittest

from httpy.Config import Config
from httpy.Response import Response
from httpy.utils import uri_to_fs


class TestUriToFs(unittest.TestCase):

    def setUp(self):
        os.mkdir('root')
        file('root/index.html', 'w')
        os.mkdir('root/__')
        os.mkdir('root/about')
        os.mkdir('root/My Documents')
        file('root/My Documents/index.html', 'w')
        os.mkdir('root/content')
        file('root/content/index.pt', 'w')

        config = {}
        config['mode'] = 'development'
        config['verbosity'] = 0
        config['site_fs_root'] = os.path.realpath('root')
        config['app_uri_root'] = '/'
        config['app_fs_root'] = os.path.realpath('root')
        config['__'] = None
        self.config = config


    def testBasic(self):
        expected = os.path.realpath('root/index.html')
        actual = uri_to_fs( self.config
                          , '/index.html'
                          , ()
                           )
        self.assertEqual(expected, actual)



    def testDefaultDocument(self):
        expected = os.path.realpath('root/index.html')
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


    def tearDown(self):
        os.system('rm -rf root')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUriToFs))
    return suite

if __name__ == '__main__':
    unittest.main()
