#!/usr/bin/env python

import unittest

from citlib.utils import CitError
from citlib.CitConn import CitConn



class TestRooms(unittest.TestCase):


    def setUp(self):
        self.cit = CitConn()
        #self.cit._listen = True
        self.cit.USER('test')
        self.cit.PASS('testing')

    def tearDown(self):
        self.cit.LOUT()
        self.cit.QUIT()


    def test_LR(self):
        rooms = self.cit.LKRA()
        mailroom = rooms[1]
        self.assertEqual(mailroom[0], 'Mail')
        self.assertEqual(mailroom[1].QR_PERMANENT,  True)
        self.assertEqual(mailroom[1].QR_PRIVATE,    False)
        self.assertEqual(mailroom[1].QR_PASSWORDED, False)
        self.assertEqual(mailroom[1].QR_GUESSNAME,  False)
        self.assertEqual(mailroom[1].QR_DIRECTORY,  False)
        self.assertEqual(mailroom[1].QR_UPLOAD,     False)
        self.assertEqual(mailroom[1].QR_DOWNLOAD,   False)
        self.assertEqual(mailroom[1].QR_VISDIR,     False)
        self.assertEqual(mailroom[1].QR_ANONONLY,   False)
        self.assertEqual(mailroom[1].QR_ANON2,      False)
        self.assertEqual(mailroom[1].QR_NETWORK,    False)
        self.assertEqual(mailroom[1].QR_PREFONLY,   True)
        self.assertEqual(mailroom[1].QR_READONLY,   True)
        self.assertEqual(mailroom[2].QR2_SYSTEM,    False)
        self.assertEqual(mailroom[2].QR2_SELFLIST,  False)
        self.assertEqual(mailroom[3], 0)
        self.assertEqual(mailroom[4], 0)
        self.assertEqual(mailroom[5].UA_KNOWN,      True)
        self.assertEqual(mailroom[5].UA_GOTOALLOWED, True)
        self.assertEqual(mailroom[5].UA_HASNEWMSGS, True)
        self.assertEqual(mailroom[5].UA_ZAPPED,     False)

    def test_LR_notLoggedIn(self):
        self.cit.LOUT()
        self.assertRaises(CitError, self.cit.LKRA)


    def test_LKRA(self):
        expected = ['Contacts', 'Mail', 'Sent Items', 'Aide',
                    'Global Address Book', 'Lobby', 'Trashcan']
        actual = [r[0] for r in self.cit.LKRA()]
        self.assertEqual(expected, actual)

    def test_LZRM(self):
        expected = []
        actual = [r[0] for r in self.cit.LZRM()]
        self.assertEqual(expected, actual)

    def test_LKRN(self):
        expected = ['Mail', 'Aide', 'Global Address Book', 'Lobby']
        actual = [r[0] for r in self.cit.LKRN()]
        self.assertEqual(expected, actual)

    def test_LKRO(self):
        expected = ['Contacts', 'Sent Items', 'Trashcan']
        actual = [r[0] for r in self.cit.LKRO()]
        self.assertEqual(expected, actual)

    def test_LPRM(self):
        expected = ['Lobby', 'Trashcan']
        actual = [r[0] for r in self.cit.LPRM()]
        self.assertEqual(expected, actual)

    def test_LRMS(self):
        expected = ['Contacts', 'Mail', 'Sent Items', 'Aide',
                    'Global Address Book', 'Lobby', 'Trashcan']
        actual = [r[0] for r in self.cit.LRMS()]
        self.assertEqual(expected, actual)




def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRooms))
    return suite

if __name__ == '__main__':
    unittest.main()
