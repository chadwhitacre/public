#!/usr/bin/env python

import unittest

from citlib import CitError
from citlib.CitConn import CitConn



class TestCitConn(unittest.TestCase):


    def setUp(self):
        self.cit = CitConn()
        self.cit.USER('test')
        self.cit.PASS('testing')

    def tearDown(self):
        self.cit.LOUT()
        self.cit.QUIT()


    # connection

    def testConnection(self):
        cit = CitConn()
        expected = '127.0.0.1'
        actual = cit._sock.getsockname()[0]
        self.assertEqual(expected, actual)
        cit._sock.close()

    def test_QUIT(self):
        cit = CitConn()
        cit.QUIT()
        expected = None
        actual = cit._sock
        self.assertEqual(expected, actual)



    # login/logout

    def test_USER(self):
        cit = CitConn()
        expected = None
        actual = cit.USER('test')
        self.assertEqual(expected, actual)
        cit.QUIT()

    def test_USER_notThere(self):
        cit = CitConn()
        self.assertRaises(CitError, cit.USER, 'not-there!')
        cit.QUIT()


    def test_PASS(self):
        cit = CitConn()
        cit.USER('test')
        expected = ('test', '3', '5', '0', '15888', '2', '1128198236')[0]
        actual = cit.PASS('testing')[0]
        self.assertEqual(expected, actual)
        cit.QUIT()

    def test_PASS_badPassword(self):
        cit = CitConn()
        actual = cit.USER('test')
        self.assertRaises(CitError, cit.PASS, 'bad password!')
        cit.QUIT()


    def test_LOUT(self):
        cit = CitConn()
        cit.USER('test')
        cit.PASS('testing')
        expected = None
        actual = cit.LOUT()
        self.assertEqual(expected, actual)
        cit.QUIT()




def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCitConn))
    return suite

if __name__ == '__main__':
    unittest.main()
