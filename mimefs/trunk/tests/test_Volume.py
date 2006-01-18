#!/usr/bin/env python

import unittest

from mimefslib import FileSystem, Volume


class TestVolume(unittest.TestCase):

    def setUp(self):
        key = open('/etc/mimefs.key').read()
        uri = "http://localhost:5370/"
        self.fs = FileSystem(uri, key)
        self.tearDown()
        self.vol = Volume(uri + self.fs.newvol())

    def testExists(self):
        vid = self.vol.list()
        expected = [vid]
        actual = self.vol.exists()
        self.assertEqual(expected, actual)

    def tearDown(self):
        for vid in self.fs.listvols():
            self.fs.rmvol(vid)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestVolume))
    return suite

if __name__ == '__main__':
    unittest.main()
