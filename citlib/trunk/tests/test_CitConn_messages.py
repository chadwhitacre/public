#!/usr/bin/env python

import unittest

from citlib.utils import CitError
from citlib.CitConn import CitConn



class Tests(unittest.TestCase):


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



    # MSGS

    def test_MSGS_basic(self):
        messages = self.cit.MSGS()
        self.assertEqual(len(messages), 0)

    def test_MSGS_badScope(self):
        self.assertRaises(ValueError, self.cit.MSGS, 'fun')





    # ENT0

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



    # DELE

    def test_DELE(self):
        r = 10
        for i in range(r):
            self.cit.ENT0(1,'',0,1,'cheese','',1,'','',message = 'BLAM!!!!!!!')
        self.assert_(len(self.cit.MSGS()) == r)
        for message in self.cit.MSGS():
            self.cit.DELE(message)
        self.assert_(len(self.cit.MSGS()) == 0)

    def test_DELE_takesInt(self):
        r = 3
        for i in range(r):
            self.cit.ENT0(1,'',0,1,'cheese','',1,'','',message = 'BLAM!!!!!!!')
        self.assert_(len(self.cit.MSGS()) == r)
        for msgnum in self.cit.MSGS():
            self.assert_(isinstance(msgnum, int))
            self.cit.DELE(msgnum)
        self.assert_(len(self.cit.MSGS()) == 0)

    def test_DELE_takesLongInt(self):
        r = 3
        for i in range(r):
            self.cit.ENT0(1,'',0,1,'cheese','',1,'','',message = 'BLAM!!!!!!!')
        self.assert_(len(self.cit.MSGS()) == r)
        for msgnum in self.cit.MSGS():
            msgnum = long(msgnum)
            self.assert_(isinstance(msgnum, long))
            self.cit.DELE(msgnum)
        self.assert_(len(self.cit.MSGS()) == 0)

    def test_DELE_otherTypesFail(self):
        self.assertRaises(TypeError, self.cit.DELE, 'foo')
        self.assertRaises(TypeError, self.cit.DELE, None)
        self.assertRaises(TypeError, self.cit.DELE, [])
        self.assertRaises(TypeError, self.cit.DELE, 4.5)




def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(Tests))
    return suite

if __name__ == '__main__':
    unittest.main()
