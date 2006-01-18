#!/usr/bin/env python
"""Basic test for mimefs.

We have to assume that mimefs is installed. Four levels of tests:

    tests using the client and testing resulting output via client
    tests using client and testing result in database itself
    tests of client itself
    tests of server w/o client


"""


import os
import unittest

from mimefslib import *



class TestBasic(unittest.TestCase):

    def setUp(self):
        key = open('/etc/mimefs.key').read()
        self.fs = FileSystem("http://localhost:5370/", key)

    def testEcho(self):
        expected = 'pong'
        actual = self.fs.ping()
        self.assertEqual(expected, actual)




def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBasic))
    return suite

if __name__ == '__main__':
    unittest.main()
