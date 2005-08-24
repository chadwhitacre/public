import os
import unittest

class httpyTestCase(unittest.TestCase):

    def removeTestSite(self):
        if not os.path.isdir('root'):
            return
        for root, dirs, files in os.walk('root', topdown=False):
            for name in dirs:
                os.rmdir(os.path.join(root, name))
            for name in files:
                os.remove(os.path.join(root, name))
        os.rmdir('root')

    _request = ( None
               , 'GET / HTTP/1.1'
               , 'GET'
               , '/'
               , '1.1'
               , [ 'Host: josemaria:8080'
                 , 'User-Agent: Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.10) Gecko/20050716 Firefox/1.0.6'
                 , 'Accept: text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5'
                 , 'Accept-Language: en-us,en;q=0.7,ar;q=0.3'
                 , 'Accept-Encoding: gzip,deflate', 'Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7'
                 , 'Keep-Alive: 300'
                 , 'Connection: keep-alive'
                  ]
                )

