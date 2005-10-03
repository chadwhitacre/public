#!/usr/bin/env python

import unittest

from citlib.utils import CitError
from citlib.CitConn import CitConn



class TestCitConn(unittest.TestCase):


    def setUp(self):
        self.cit = CitConn()
        self.cit._listen = True
        self.cit.USER('test')
        self.cit.PASS('testing')

    def tearDown(self):
        self.cit.LOUT()
        self.cit.QUIT()



    def test_LKRN(self):
        self.cit.LKRN()

    def foo(self):
        expected = ('0', 'Main Floor', '17')[:2]
        floors = self.cit.LKRN()
        self.assert_(len(floors) == 1)
        actual = floors[0][:2]
        self.assertEqual(expected, actual)

    def test_LKRN_notLoggedIn(self):
        self.cit.LOUT()
        self.assertRaises(CitError, self.cit.LFLR)
        self.cit.USER('test')
        self.cit.PASS('testing')





def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCitConn))
    return suite

if __name__ == '__main__':
    unittest.main()
