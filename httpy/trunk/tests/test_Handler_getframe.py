#!/usr/bin/env python

import os
import unittest

from simpletal import simpleTAL

from HandlerTestCase import HandlerTestCase


dummy_frame = """\
<html metal:define-macro="frame">
    foo
</html>"""


class TestFrame(HandlerTestCase):

    setpath = False

    def buildTestSite(self):
        os.mkdir('root')
        os.mkdir('root/__')
        file_ = open('root/__/frame.pt','w')
        file_.write(dummy_frame)
        file_.close()

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

    def testEmptyFrame(self):
        file('root/__/frame.pt', 'w') # overwrite with empty file
        expected = None
        actual = self.handler._getframe()
        self.assertEqual(expected, actual)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFrame))
    return suite

if __name__ == '__main__':
    unittest.main()
