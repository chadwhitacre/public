import os
import sys
sys.path.insert(0, os.path.realpath('..'))

import httpy
import unittest

default_server_config, default_handler_config = httpy.parse_config('')
default_request = ( None
                  , 'GET / HTTP/1.1'
                  , 'GET'
                  , '/'
                  , '1.1'
                  , ['Host: josemaria:8080', 'User-Agent: Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.10) Gecko/20050716 Firefox/1.0.6', 'Accept: text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5', 'Accept-Language: en-us,en;q=0.7,ar;q=0.3', 'Accept-Encoding: gzip,deflate', 'Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Keep-Alive: 300', 'Connection: keep-alive']
                   )
from medusa import http_server

class TestPathInfo(unittest.TestCase):

    def setUp(self):

        # rebuild a temporary website tree in ./root
        os.system('rm -rf root')
        os.system('tar jxf data/path_info.tbz')

        # handler
        self.request = http_server.http_request(*default_request)
        self.handler = httpy.handler(**default_handler_config)

    def testRootIsSetAsExpected(self):
        self.assertEqual(self.handler.root, os.path.realpath('./root'))

    def testBasic(self):
        self.request.uri = '/about'
        self.handler.path_info(self.request)
        expected = (os.path.realpath('root/about/index.html'), '/about')
        actual = (self.request.path, self.request.uri)
        self.assertEqual(expected, actual)

    def testEncodedURIGetsUnencoded(self):
        self.request.uri = '/My%20Documents'
        self.handler.path_info(self.request)
        expected = (os.path.realpath('root/My Documents/index.pt'), '/My%20Documents')
        actual = (self.request.path, self.request.uri)
        self.assertEqual(expected, actual)

    def testDoubleRootRaisesError(self):
        self.request.uri = '//about'
        self.assertRaises(httpy.RequestError, self.handler.path_info, self.request)

    def tearDown(self):
        os.system('rm -rf root')
        pass


if __name__ == '__main__':
    unittest.main()