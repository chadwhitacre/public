#!/usr/bin/env python

import unittest

from citlib.CitServer import CitError, CitServer



class TestCitServer(unittest.TestCase):

    def setUp(self):
        self.cit = CitServer()

    def tearDown(self):
        self.cit._sock.close()


    def testBasic(self):
        expected = '127.0.0.1'
        actual = self.cit._sock.getsockname()[0]
        self.assertEqual(expected, actual)

    def test_USER(self):
        expected = None
        actual = self.cit.USER('test')
        self.assertEqual(expected, actual)

    def test_USER_notThere(self):
        self.assertRaises(CitError, self.cit.USER, 'not-there!')


    def test_PASS(self):
        self.cit.USER('test')
        expected = ('test', '3', '5', '0', '15888', '2', '1128198236')[0]
        actual = self.cit.PASS('testing')[0]
        self.assertEqual(expected, actual)

    def test_PASS_badPassword(self):
        actual = self.cit.USER('test')
        self.assertRaises(CitError, self.cit.USER, 'bad password!')



    def test_LOUT(self):
        self.cit.USER('test')
        self.cit.PASS('testing')
        expected = None
        actual = self.cit.LOUT()
        self.assertEqual(expected, actual)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCitServer))
    return suite

if __name__ == '__main__':
    unittest.main()