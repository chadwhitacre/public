#!/usr/bin/env python

import os
import unittest

from httpy.HandlerRequestMixin import HandlerRequestMixin
from httpy.Response import Response
from httpyTestCase import httpyTestCase


# later
DUMMY_APP = """\
class Transaction:
    def __init__(self, config):
        return config
    def process(self, request):
        raise "heck" """
#file('root/app1/app.py', 'w').write(DUMMY_APP)


class TestTranslate(httpyTestCase):

    server = False
    siteroot = os.path.join(os.path.realpath('.'),'root')


    def setUp(self):
        httpyTestCase.setUp(self)
        self.mixin = HandlerRequestMixin()

    def buildTestSite(self):
        os.mkdir('root')
        file('root/index.html', 'w').write('hello world')
        os.mkdir('root/app1')
        os.mkdir('root/app2')
        os.mkdir('root/app2/__')


    def testBasic(self):
        root = self.siteroot
        apps = []
        path = '/'

        expected = (self.siteroot, None)
        actual = self.mixin.translate(root, apps, path)
        self.assertEqual(expected, actual)

    def testAppNotThereRaises404(self):
        root = self.siteroot
        apps = ['/not-there']
        path = '/not-there'

        try:
            self.mixin.translate(root, apps, path)
        except Response, response:
            self.assertEqual(response.code, 404)

    def testNonWebsiteRootApp(self):
        root = self.siteroot
        apps = ['/app1']
        path = '/app1'

        expected = (os.path.join(self.siteroot, 'app1'), None)
        actual = self.mixin.translate(root, apps, path)
        self.assertEqual(expected, actual)

    def testOtherAppsAvailableButNotMatchedReturnsRoot(self):
        root = self.siteroot
        apps = ['/app1']
        path = '/not-there'

        expected = (self.siteroot, None)
        actual = self.mixin.translate(root, apps, path)
        self.assertEqual(expected, actual)

    def testEtcPasswdRaises400(self):
        root = self.siteroot
        apps = []
        path = '/../../../../../../../../../../etc/master.passwd'

        try:
            self.mixin.translate(root, apps, path)
        except Response, response:
            self.assertEqual(response.code, 403)

    def testSubdirStillMatches(self):
        root = self.siteroot
        apps = ['/app1']
        path = '/app1/index.html'

        expected = (os.path.join(self.siteroot, 'app1'), None)
        actual = self.mixin.translate(root, apps, path)
        self.assertEqual(expected, actual)

    def testAppHasMagicDirectory(self):
        root = self.siteroot
        apps = ['/app2']
        path = '/app2'

        expected = ( os.path.join(self.siteroot, 'app2')
                   , os.path.join(self.siteroot, 'app2', '__')
                    )
        actual = self.mixin.translate(root, apps, path)
        self.assertEqual(expected, actual)

    def testButDirectlyAccessingItRaises404(self):
        root = self.siteroot
        apps = ['/app2']
        path = '/app2/__'

        try:
            self.mixin.translate(root, apps, path)
        except Response, response:
            self.assertEqual(response.code, 404)

    def testSubdirsToo(self):
        root = self.siteroot
        apps = ['/app2']
        path = '/app2/__/app.py' # Doesn't actually exist, proving we are
                                 # catching it here.
        try:
            self.mixin.translate(root, apps, path)
        except Response, response:
            self.assertEqual(response.code, 404)



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTranslate))
    return suite

if __name__ == '__main__':
    unittest.main()
