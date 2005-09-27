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


    # fail
    # ====

    def testFailInDevMode(self):
        task = DUMMY_TASK()
        task.dev_mode = True
        task.channel = StubChannel()
        try:
            raise Exception("Yarrr!")
        except:
            task.fail()

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
        actual = task.channel.getvalue().splitlines()
        actual = actual[:1] + actual[2:7] + actual[-1:]
        self.assertEqual(expected, actual)

    def testFailInDepMode(self):
        task = DUMMY_TASK()
        task.dev_mode = False
        task.channel = StubChannel()
        try:
            raise Exception("Yarrr!")
        except:
            task.fail()

        expected = [ "HTTP/1.0 500 Internal Server Error"
                   , "Content-Length: 25"
                   , "Content-Type: text/plain"
                   , ""
                   , "Internal Server Error"
                   , ""
                    ]
        actual = task.channel.getvalue().splitlines()
        self.assertEqual(expected, actual)


    # check_mtimes
    # ============

    def testMtimesBasic(self):
        pass # Boooooo!


    # service
    # =======

    def testServiceAtLeastOnceForCryingOutLoud(self):
        task = DUMMY_TASK()
        task.service()
        expected = [ "HTTP/1.0 403 Forbidden"
                   , "content-length: 48"
                   , "content-type: text/plain"
                   , "server: stub server"
                   , ""
                   , "Request forbidden -- authorization will not help"
                    ]
        expected = '\r\n'.join(expected)
        actual = task.channel.getvalue()
        self.assertEqual(expected, actual)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTask))
    return suite

if __name__ == '__main__':
    unittest.main()
