#!/usr/bin/env python

# Make sure we can find the module we want to test.
# =================================================

import os
import sys
if __name__ == '__main__':
    sys.path.insert(0, os.path.realpath('..'))


# Import some modules.
# ====================

import httpy
import unittest
from medusa import http_server
from httpyTestCase import httpyTestCase
from simpletal import simpleTAL


# Define the site to test against.
# ================================

dummy_frame = """\
<html metal:define-macro="frame">
    foo
</html>"""

def buildTestSite():
    os.mkdir('root')
    os.mkdir('root/__')
    file_ = open('root/__/frame.pt','w')
    file_.write(dummy_frame)
    file_.close()


# Define our testing class.
# =========================

class TestFrame(httpyTestCase):

    def setUp(self):

        # [re]build a temporary website tree in ./root
        self.removeTestSite()
        buildTestSite()

        # handler
        self.request = http_server.http_request(*self._request)
        handler_config = httpy.parse_config('')[1]
        self.handler = httpy.handler(**handler_config)

    def testHasFrame(self):
        file_ = open('root/__/frame.pt','r')
        expected = simpleTAL.compileXMLTemplate(file_).macros['frame']
        actual = self.handler._getframe()
        self.assertEqual(type(expected), type(actual))
        self.assertEqual(str(expected), str(actual))

    def testNoFrame(self):
        os.remove('root/__/frame.pt')
        expected = None
        actual = self.handler._getframe()
        self.assertEqual(expected, actual)

    def tearDown(self):
        self.removeTestSite()
        pass


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFrame))
    return suite

if __name__ == '__main__':
    unittest.main()
