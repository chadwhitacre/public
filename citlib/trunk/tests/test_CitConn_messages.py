#!/usr/bin/env python

import unittest

from citlib.utils import CitError
from citlib.CitConn import CitConn



class Tests(unittest.TestCase):


    def setUp(self):
        self.cit = CitConn()
        self.cit._listen = 0
        self.cit.USER('test')
        self.cit.PASS('testing')

        # bootstrapping a bit here
        self.rmmsgs()

    def tearDown(self):
        self.cit.LOUT()
        self.cit.QUIT()

    def addmsg(self):
        self.cit.ENT0(1,'',0,1,'cheese','',1,'','',message = 'BLAM!!!!!!!')

    def addmsgs(self, r):
        for i in range(r):
            self.addmsg()
        self.assert_(len(self.cit.MSGS()) == r)

    def rmmsgs(self):
        for msgnum in self.cit.MSGS():
            self.cit.DELE(msgnum)



    # MSGS

    def test_MSGS_basic(self):
        messages = self.cit.MSGS()
        self.assertEqual(len(messages), 0)

    def test_MSGS_badScope(self):
        self.assertRaises(ValueError, self.cit.MSGS, 'fun')

    def test_MSGS_needNumNoNum(self):
        self.assertRaises(ValueError, self.cit.MSGS, 'last')

    def test_MSGS_needNumBadNum(self):
        self.assertRaises(ValueError, self.cit.MSGS, 'last', 'fooey')

    def test_MSGS_needNumGoodNum(self):
        self.addmsgs(5)
        msgs = self.cit.MSGS('all')
        self.assertEqual(len(msgs), 5)
        msgs = self.cit.MSGS('last', 2)
        self.assertEqual(len(msgs), 2)

    def test_MSGS_paramsBasic(self):
        self.addmsgs(4)
        msgs = self.cit.MSGS('all', q={})
        self.assertEqual(len(msgs), 4)
        self.cit.ENT0(1,'',0,1,'teehee','',1,'','',message = 'YES!!!!!!!')
        self.assertEqual(len(self.cit.MSGS()), 5)
        msgs = self.cit.MSGS('all', q={'subj':'teehee'})
        self.assertEqual(len(msgs), 1)
        msgs = self.cit.MSGS('all', q={'subj':'cheese'})
        self.assertEqual(len(msgs), 4)

    def _test_MSGS_paramsMultiple(self):
        # no obvious second parameter to use at this point
        pass

    def test_MSGS_headers_basic(self):
        self.addmsgs(2)
        expected = [ (445, 1128604557, 'test', 'josemaria', 'test@zetadev.com',
                      'cheese', '')
                   , (446, 1128604557, 'test', 'josemaria', 'test@zetadev.com',
                      'cheese', '')
                    ][1][5]
        actual = self.cit.MSGS(headers=True)[1][5]
        self.assertEqual(expected, actual)




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
        self.addmsgs(3)
        for message in self.cit.MSGS():
            self.cit.DELE(message)
        self.assert_(len(self.cit.MSGS()) == 0)

    def test_DELE_takesInt(self):
        self.addmsgs(1)
        for msgnum in self.cit.MSGS():
            self.assert_(isinstance(msgnum, int))
            self.cit.DELE(msgnum)
        self.assert_(len(self.cit.MSGS()) == 0)

    def test_DELE_takesLongInt(self):
        self.addmsgs(1)
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
