import os
import sys
sys.path.insert(0, os.path.realpath('..'))

import httpy
import stat
import unittest
from medusa import http_server
from httpyTestCase import httpyTestCase

default_server_config, default_handler_config = httpy.parse_config('')
default_request = ( None
                  , 'GET / HTTP/1.1'
                  , 'GET'
                  , '/'
                  , '1.1'
                  , ['Host: josemaria:8080', 'User-Agent: Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.10) Gecko/20050716 Firefox/1.0.6', 'Accept: text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5', 'Accept-Language: en-us,en;q=0.7,ar;q=0.3', 'Accept-Encoding: gzip,deflate', 'Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Keep-Alive: 300', 'Connection: keep-alive']
                   )

def buildTestSite():
    os.mkdir('root')
    file('root/index.html','w')
    os.mkdir('root/about')
    os.mkdir('root/My Documents')
    file('root/My Documents/index.html','w')


class TestPathInfo(httpyTestCase):

    def setUp(self):

        # [re]build a temporary website tree in ./root
        self.removeTestSite()
        buildTestSite()

        # handler
        self.request = http_server.http_request(*default_request)
        self.handler = httpy.handler(**default_handler_config)

    def testRootIsSetAsExpected(self):
        self.assertEqual(self.handler.root, os.path.realpath('./root'))

    def testBasic(self):
        self.request.uri = '/index.html'
        self.handler.path_info(self.request)
        expected = (os.path.realpath('root/index.html'), '/index.html')
        actual = (self.request.path, self.request.uri)
        self.assertEqual(expected, actual)

    def testDefaultDocument(self):
        self.request.uri = '/'
        self.handler.path_info(self.request)
        expected = (os.path.realpath('root/index.html'), '/')
        actual = (self.request.path, self.request.uri)
        self.assertEqual(expected, actual)

    def testEncodedURIGetsUnencoded(self):
        self.request.uri = '/My%20Documents'
        self.handler.path_info(self.request)
        expected = (os.path.realpath( 'root/My Documents/index.html')
                                   , '/My%20Documents'
                                     )
        actual = (self.request.path, self.request.uri)
        self.assertEqual(expected, actual)

    def testDoubleRootRaisesBadRequest(self):
        self.request.uri = '//index.html'
        self.assertRaises( httpy.RequestError
                         , self.handler.path_info
                         , self.request
                          )
        try:
            self.handler.path_info(self.request)
        except httpy.RequestError, err:
            self.assertEqual(err.code, 400)

    def testNoDefaultRaisesForbidden(self):
        self.request.uri = '/about'
        self.assertRaises( httpy.RequestError
                         , self.handler.path_info
                         , self.request
                          )
        try:
            self.handler.path_info(self.request)
        except httpy.RequestError, err:
            self.assertEqual(err.code, 403)

    def testNotThereRaisesNotFound(self):
        self.request.uri = '/not-there'
        self.assertRaises( httpy.RequestError
                         , self.handler.path_info
                         , self.request
                          )
        try:
            self.handler.path_info(self.request)
        except httpy.RequestError, err:
            self.assertEqual(err.code, 404)

    def testOutsideRootRaisesBadRequest(self):
        self.request.uri = '/../../../../../../../root'
        self.assertRaises( httpy.RequestError
                         , self.handler.path_info
                         , self.request
                          )
        try:
            self.handler.path_info(self.request)
        except httpy.RequestError, err:
            self.assertEqual(err.code, 400)

    def tearDown(self):
        self.removeTestSite()



if __name__ == '__main__':
    unittest.main()
