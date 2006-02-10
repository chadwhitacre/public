#!/usr/bin/env python

import os
import unittest
from StringIO import StringIO

from httpy._zope.server.adjustments import default_adj

from httpy.Config import Config
from httpy.Request import ZopeRequest
from httpy.Response import Response
from httpy.Task import Task

from TestCaseHttpy import TestCaseHttpy
from utils import DUMMY_TASK, StubChannel


class TestCase(TestCaseHttpy):

    def setUp(self):
        TestCaseHttpy.setUp(self)
        self.task = DUMMY_TASK()
        self.task.server.deploy_mode = True


    # fail
    # ====

    def testFailInNonDeploymentMode(self):
        self.task.server.deploy_mode = False
        try:
            raise StandardError("Yarrr!")
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
                   , 'StandardError: Yarrr!'
                    ]
        actual = self.task.channel.getvalue().splitlines()
        actual = actual[:1] + actual[2:7] + actual[-1:]
        self.assertEqual(expected, actual)

    def testFailInDepMode(self):
        try:
            raise StandardError("Yarrr!")
        except:
            self.task.fail()

        expected = [ "HTTP/1.0 500 Internal Server Error"
                   , "Content-Length: 21"
                   , "Content-Type: text/plain"
                   , ""
                   , "Internal Server Error"
                    ]
        actual = self.task.channel.getvalue().splitlines()
        self.assertEqual(expected, actual)


    # service
    # =======

    def testServiceAtLeastOnceForCryingOutLoud(self):
        self.task.service()
        expected = [ "HTTP/1.0 403 Forbidden"
                   , "content-length: 48"
                   , "content-type: text/plain"
                   , "server: stub server"
                   , ""
                   , "Request forbidden -- authorization will not help"
                    ]
        expected = '\r\n'.join(expected)
        actual = self.task.channel.getvalue()
        self.assertEqual(expected, actual)

    def testExceptionInDeliverStillProducesResult(self):
        def bad_deliver(self, request):
            raise Exception("MUAHAHAHAHAHHAHA!!!!!!!!!!!!!!!")
        self.task.deliver = bad_deliver
        self.task.service()

        expected = [ "HTTP/1.0 500 Internal Server Error"
                   , "Content-Length: 21"
                   , "Content-Type: text/plain"
                   , ""
                   , "Internal Server Error"
                    ]
        expected = '\r\n'.join(expected)
        actual = self.task.channel.getvalue()
        self.assertEqual(expected, actual)




def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCase))
    return suite

if __name__ == '__main__':
    unittest.main()
