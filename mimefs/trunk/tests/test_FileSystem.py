#!/usr/bin/env python

import unittest

from mimefslib import FileSystem


class TestFileSystem(unittest.TestCase):

    def setUp(self):
        key = open('/etc/mimefs.key').read()
        self.fs = FileSystem("http://localhost:5370/", key)
        self.tearDown()
        #self.conn = psycopg.connect('dbname=mimefs_0')
        #self.curs = self.conn.cursor()

    def testNewVol(self):
        vid = self.fs.newvol()
        expected = [vid]
        actual = self.fs.listvols()
        self.assertEqual(expected, actual)

    def testRmVol(self):
        vid = self.fs.newvol()
        self.fs.rmvol(vid)
        expected = []
        actual = self.fs.listvols()
        self.assertEqual(expected, actual)

    def testListVols(self):
        vids = []
        for i in range(10):
            vid = self.fs.newvol()
            vids.append(vid)
        expected = vids
        actual = self.fs.listvols()
        self.assertEqual(expected, actual)

    def tearDown(self):
        for vid in self.fs.listvols():
            self.fs.rmvol(vid)
        #self.conn.close()


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFileSystem))
    return suite

if __name__ == '__main__':
    unittest.main()
