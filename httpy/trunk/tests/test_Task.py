#!/usr/bin/env python

import os
import unittest
from StringIO import StringIO

from httpy._zope.server.adjustments import default_adj

from httpy.Config import ServerConfig
from httpy.Request import ZopeRequest
from httpy.Response import Response
from httpy.Task import Task

from TestCaseHttpy import TestCaseHttpy


DUMMY_APP = """\
from httpy.Response import Response
class Transaction:
    def __init__(self, config):
        pass
    def process(self, request):
        raise Response(200)
"""


from utils import DUMMY_TASK, StubChannel


class TestTask(TestCaseHttpy):

    def setUp(self):
        self.task = DUMMY_TASK()
        TestCaseHttpy.setUp(self)


    # configure
    # =========

    def testServerConfigure(self):
        config = ServerConfig(['-v22','-mdeployment','-rroot'])
        expected = {}
        expected['mode'] = 'deployment'
        expected['verbosity'] = 22
        expected['site_fs_root'] = os.path.realpath('root')
        expected['app_uri_root'] = '/'
        expected['app_fs_root'] = os.path.realpath('root')
        expected['__'] = None
        actual = self.task.configure(config)
        self.assertEqual(expected, actual)


    # fail
    # ====

    def testFailInDevMode(self):
        self.task.dev_mode = True
        self.task.channel = StubChannel()
        try:
            raise Exception("Yarrr!")
        except:
            self.task.fail()

        # Traceback and content length depend on incidental circumstances.
        expected = [ "HTTP/1.0 500 Internal Server Error"
                   # "Content-Length: x"
                   , "Content-Type: text/plain"
                   , ""
                   , "Internal Server Error"
                   , ""
                   , "Traceback (most recent call last):"
                   # ...
                   , 'Exception: Yarrr!'
                    ]
        actual = self.task.channel.getvalue().splitlines()
        actual = actual[:1] + actual[2:7] + actual[-1:]
        self.assertEqual(expected, actual)

    def testFailInDepMode(self):
        self.task.dev_mode = False
        self.task.channel = StubChannel()
        try:
            raise Exception("Yarrr!")
        except:
            self.task.fail()

        expected = [ "HTTP/1.0 500 Internal Server Error"
                   , "Content-Length: 25"
                   , "Content-Type: text/plain"
                   , ""
                   , "Internal Server Error"
                   , ""
                    ]
        actual = self.task.channel.getvalue().splitlines()
        self.assertEqual(expected, actual)


    # process
    # =======

    def testProcessAtLeastOnceForCryingOutLoud(self):
        expected = 403 # we don't have a site set up
        try:
            import sys
            _path = sys.path[:]
            sys.path.insert(0, self.task.config.__)
            try:
                self.task.process()
            finally:
                sys.path = _path
        except Response, response:
            actual = response.code
        self.assertEqual(expected, actual)

    def testProcessMore(self):
        os.mkdir('root/fooapp')
        os.mkdir('root/fooapp/__')
        file('root/fooapp/__/app.py','w').write(DUMMY_APP)

        request = ZopeRequest(default_adj)
        request.received("GET /fooapp/ HTTP/1.1\r\n\r\n")
        task = Task(StubChannel(), request)

        config = ServerConfig(['--root','root','-mdevelopment'])
        task.config = task.configure(config)

        expected = 200
        try:
            import sys
            _path = sys.path[:]
            sys.path.insert(0, task.config.__)
            try:
                task.process()
            finally:
                sys.path = _path
        except Response, response:
            actual = response.code
        self.assertEqual(expected, actual)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTask))
    return suite

if __name__ == '__main__':
    unittest.main()
