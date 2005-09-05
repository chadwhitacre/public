#!/usr/bin/env python

import os
import unittest

#from RequestTestCase import RequestTestCase
RequestTestCase = unittest.TestCase


class TestRequest(RequestTestCase):

    def testBasic(self):

        pass




def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRequest))
    return suite

if __name__ == '__main__':
    unittest.main()
