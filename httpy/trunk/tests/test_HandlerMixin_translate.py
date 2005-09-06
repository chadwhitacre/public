#!/usr/bin/env python

import os
import unittest

from httpy.HandlerMixin import HandlerMixin
from httpyTestCase import httpyTestCase


class TestTranslate(httpyTestCase):

    server = False
    siteroot = os.path.join(os.path.realpath('.'),'root')


    def setUp(self):
        httpyTestCase.setUp(self)
        self.mixin = HandlerMixin()

    def buildTestSite(self):
        os.mkdir('root')
        file('root/index.html', 'w').write('hello world')
        os.mkdir('root/app1')

    def testBasic(self):
        root = self.siteroot
        apps = []
        path = '/'

        expected = (self.siteroot, None)
        actual = self.mixin.translate(root, apps, path)
        self.assertEqual(expected, actual)

    def testOtherApp(self):
        root = self.siteroot
        apps = []
        path = '/app1'

        expected = (self.siteroot, None)
        actual = self.mixin.translate(root, apps, path)
        self.assertEqual(expected, actual)



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTranslate))
    return suite

if __name__ == '__main__':
    unittest.main()
