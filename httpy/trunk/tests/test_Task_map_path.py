#!/usr/bin/env python

import os
import unittest

from httpy.Response import Response

from TestCaseHttpy import TestCaseHttpy

DUMMY_APP = """\
class Transaction:
    def __init__(self, config):
        return config
    def process(self, request):
        raise "heck" """


from TestCaseTask import DUMMY_TASK


class TestMapPath(TestCaseHttpy):

    server = False
    siteroot = os.path.join(os.path.realpath('.'),'root')


    def setUp(self):
        TestCaseHttpy.setUp(self)
        self.task = DUMMY_TASK()
        self.SUCCESS = ( '/app1'
                       , os.path.join(self.siteroot, 'app1')
                       , os.path.join(self.siteroot, 'app1', '__')
                        )


    def buildTestSite(self):
        os.mkdir('root')
        file('root/index.html', 'w').write('Greetings, program!')
        os.mkdir('root/app1')
        os.mkdir('root/app1/__')
        os.mkdir('root/app2')


    def testBasic(self):
        root = self.siteroot
        apps = ('/',)
        path = '/'

        expected = ('/', self.siteroot, None)
        actual = self.task.map_path(root, apps, path)
        self.assertEqual(expected, actual)

    def testAppNotThereRaises404(self):
        root = self.siteroot
        apps = ('/not-there','/')
        path = '/not-there'

        try:
            self.task.map_path(root, apps, path)
        except Response, response:
            self.assertEqual(response.code, 404)

    def testNonRootAppWithNoMagicDirectoryRaises500(self):
        root = self.siteroot
        apps = ('/app2','/')
        path = '/app2'

        try:
            self.task.map_path(root, apps, path)
        except Response, response:
            self.assertEqual(response.code, 500)

    testButRootAppNeedntHaveAMagicDirectory = testBasic

    def testNonWebsiteRootApp(self):
        root = self.siteroot
        apps = ('/app1','/')
        path = '/app1'

        expected = self.SUCCESS
        actual = self.task.map_path(root, apps, path)
        self.assertEqual(expected, actual)

    def testOtherAppsAvailableButNotMatchedReturnsRoot(self):
        root = self.siteroot
        apps = ('/app1','/')
        path = '/not-there'

        expected = ('/', self.siteroot, None)
        actual = self.task.map_path(root, apps, path)
        self.assertEqual(expected, actual)

    def testEtcPasswdRaises403(self):
        root = self.siteroot
        apps = ('/',)
        path = '/../../../../../../../../../../etc/master.passwd'

        try:
            self.task.map_path(root, apps, path)
        except Response, response:
            self.assertEqual(response.code, 403)

    def testSubdirStillMatches(self):
        root = self.siteroot
        apps = ('/app1', '/')
        path = '/app1/foo/bar.html'

        expected = self.SUCCESS
        actual = self.task.map_path(root, apps, path)
        self.assertEqual(expected, actual)

    def testAppHasMagicDirectory(self):
        root = self.siteroot
        apps = ('/app1', '/')
        path = '/app1'

        expected = self.SUCCESS
        actual = self.task.map_path(root, apps, path)
        self.assertEqual(expected, actual)

    def testButDirectlyAccessingItRaises404(self):
        root = self.siteroot
        apps = ('/app1', '/')
        path = '/app1/__'

        try:
            self.task.map_path(root, apps, path)
        except Response, response:
            self.assertEqual(response.code, 404)

    def testSubdirsToo(self):
        root = self.siteroot
        apps = ('/app1', '/')
        path = '/app1/__/app.py' # Doesn't actually exist, proving we are
                                 # catching it here.
        try:
            self.task.map_path(root, apps, path)
        except Response, response:
            self.assertEqual(response.code, 404)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMapPath))
    return suite

if __name__ == '__main__':
    unittest.main()
