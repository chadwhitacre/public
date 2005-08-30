import os
import unittest

from medusa import http_server

from httpy.Configuration import ConfigError
from httpy.Configuration import Configuration
from httpy.Handler import Handler


class HandlerTestCase(unittest.TestCase):

    setpath = True

    def setUp(self):

        # [re]build a temporary website tree in ./root
        self.removeTestSite()
        self.buildTestSite()

        # request and handler
        self.request = http_server.http_request(*self._request)
        try:
            config = Configuration(['--r','root','--mode','development'])
        except ConfigError, error:
            print error.msg
        self.handler = Handler(**config.handler)

        if self.setpath:
            self.handler._setpath(self.request)

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

    def neuter_traceback(self, tb):
        """Given a traceback, return just the system-independent lines.
        """
        tb_list = tb.split(os.linesep)
        if not tb_list[-1]:
            tb_list = tb_list[:-1]
        neutered = []
        for i in range(0,len(tb_list),2):
            neutered.append(tb_list[i])
        neutered.append(tb_list[-1])
        return os.linesep.join(neutered)


    def tearDown(self):
        self.removeTestSite()
