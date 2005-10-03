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

        # bootstrapping a bit here
        for message in self.cit.MSGS():
            self.cit.DELE(message)

    def tearDown(self):
        self.cit.LOUT()
        self.cit.QUIT()


    def test_MSGS(self):
        messages = self.cit.MSGS()
        self.assertEqual(len(messages), 0)


    def test_ENT0(self):
        self.cit.ENT0( 1
                     , ''
                     , 0
                     , 1
                     , 'cheese'
                     , ''
                     , 1
                     , ''
                     , ''
                     , message = 'BLAM!!!!!!!!!!!'
                      )
        messages = self.cit.MSGS()
        self.assertEqual(len(messages), 1)


    def test_DELE(self):
        self.cit.ENT0(1,'',0,1,'cheese','',1,'','',message = 'BLAM!!!!!!!!!!!')
        self.cit.ENT0(1,'',0,1,'cheese','',1,'','',message = 'BLAM!!!!!!!!!!!')
        self.cit.ENT0(1,'',0,1,'cheese','',1,'','',message = 'BLAM!!!!!!!!!!!')
        self.cit.ENT0(1,'',0,1,'cheese','',1,'','',message = 'BLAM!!!!!!!!!!!')
        self.cit.ENT0(1,'',0,1,'cheese','',1,'','',message = 'BLAM!!!!!!!!!!!')
        self.cit.ENT0(1,'',0,1,'cheese','',1,'','',message = 'BLAM!!!!!!!!!!!')
        self.cit.ENT0(1,'',0,1,'cheese','',1,'','',message = 'BLAM!!!!!!!!!!!')
        self.cit.ENT0(1,'',0,1,'cheese','',1,'','',message = 'BLAM!!!!!!!!!!!')
        self.cit.ENT0(1,'',0,1,'cheese','',1,'','',message = 'BLAM!!!!!!!!!!!')
        self.cit.ENT0(1,'',0,1,'cheese','',1,'','',message = 'BLAM!!!!!!!!!!!')
        self.assert_(len(self.cit.MSGS()) >= 10)
        for message in self.cit.MSGS():
            self.cit.DELE(message)
        self.assert_(len(self.cit.MSGS()) == 0)




def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCitConn))
    return suite

if __name__ == '__main__':
    unittest.main()
