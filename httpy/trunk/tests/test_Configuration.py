#!/usr/bin/env python

import os
import unittest

from HandlerTestCase import HandlerTestCase



class TestConfiguration(HandlerTestCase):

    def buildTestSite():
        os.mkdir('root')
        file('root/index.html', 'w')
        os.mkdir('root/about')
        os.mkdir('root/__')
        file_ = open('root/__/context.py', 'w')
        file_.write(dummy_context)
        file_.close()
        file_ = open('root/foo.pt', 'w')
        file_.write(dummy_tal)
        file_.close()

    def testBasic(self):
        pass


def tes_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGetTemplate))
    return suite

if __name__ == '__main__':
    unittest.main()
