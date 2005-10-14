#!/usr/bin/env python

import os
import unittest

from httpy.Response import Response
from httpy.Task import Task

from TestCaseHttpy import TestCaseHttpy
from utils import DUMMY_APP, StubChannel


class TestTaskProcess(TestCaseHttpy):

    testsite = [ ('/index.html', 'Greetings, program!')
               ,  '/app1'
               ,  '/app1/__'
               , ('/app1/__/app.py', DUMMY_APP)
               ,  '/app2'
                ]


    def testBasic(self):
        request = self.make_request('/index.html', Zope=True)
        task = Task(StubChannel(), request)
        try:
            task.respond()
        except Response, response:
            pass
        expected = "Greetings, program!"
        actual = response.body
        self.assertEqual(expected, actual)

    def testAppNotThereRaises404(self):
        request = self.make_request('/not-there', Zope=True)
        task = Task(StubChannel(), request)
        try:
            task.respond()
        except Response, response:
            self.assertEqual(response.code, 404)

    def testNonRootAppWithNoMagicDirectoryRaises500(self):
        request = self.make_request('/app1', Zope=True)
        task = Task(StubChannel(), request)
        os.remove(self.convert_path('root/app1/__/app.py'))
        os.remove(self.convert_path('root/app1/__/app.pyc'))
        os.rmdir(self.convert_path('root/app1/__'))
        try:
            task.respond()
        except Response, response:
            self.assertEqual(response.code, 500)

    testButRootAppNeedntHaveAMagicDirectory = testBasic

    def testSubdirStillMatches(self):
        request = self.make_request('/app1/foo/bar.html', Zope=True)
        task = Task(StubChannel(), request)
        try:
            task.respond()
        except Response, response:
            self.assertEqual(response.code, 200)

    def testDirectlyAccessingMagicDirectoryRaises404(self):
        request = self.make_request('/app1/__', Zope=True)
        task = Task(StubChannel(), request)
        try:
            task.respond()
        except Response, response:
            self.assertEqual(response.code, 404)

    def testOrAnythingUnderTheMagicDirectoryToo(self):
        request = self.make_request('/app1/__/blah/blah/blah', Zope=True)
        task = Task(StubChannel(), request)
        try:
            task.respond()
        except Response, response:
            self.assertEqual(response.code, 404)


    # find_app

    def testEtcPasswdCaughtByFindApp(self):
        request = self.make_request('../../../../../../../../../../etc/master.passwd', Zope=True)
        task = Task(StubChannel(), request)
        expected = [ "HTTP/1.0 500 Internal Server Error"
                   , "Content-Length: 25"
                   , "Content-Type: text/plain"
                   , ""
                   , "Internal Server Error"
                   , ""
                   , ""
                    ]
        expected = '\r\n'.join(expected)
        actual = task.channel.getvalue()
        self.assertEqual(expected, actual)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTaskProcess))
    return suite

if __name__ == '__main__':
    unittest.main()
