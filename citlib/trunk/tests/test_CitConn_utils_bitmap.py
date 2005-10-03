#!/usr/bin/env python

import unittest

from citlib.utils import bitmap, Bucket, bitbucket


class TestUtilsBitmap(unittest.TestCase):

    def testBasic(self):
        expected = { 8192: False
                   , 4096: False
                   , 2048: False
                   , 1024: False
                   ,  512: False
                   ,  256: False
                   ,  128: False
                   ,   64: False
                   ,   32: False
                   ,   16: False
                   ,    8: False
                   ,    4: False
                   ,    2: False
                   ,    1: True
                    }
        actual = bitmap(1)
        self.assertEqual(expected, actual)

    def testLow(self):
        expected = { 8192: False
                   , 4096: False
                   , 2048: False
                   , 1024: False
                   ,  512: False
                   ,  256: False
                   ,  128: False
                   ,   64: False
                   ,   32: False
                   ,   16: False
                   ,    8: False
                   ,    4: False
                   ,    2: False
                   ,    1: False
                    }
        actual = bitmap(0)
        self.assertEqual(expected, actual)

    def testLowMinusOne(self):
        self.assertRaises(ValueError, bitmap, -1)

    def testHigh(self):
        expected = { 8192: True
                   , 4096: True
                   , 2048: True
                   , 1024: True
                   ,  512: True
                   ,  256: True
                   ,  128: True
                   ,   64: True
                   ,   32: True
                   ,   16: True
                   ,    8: True
                   ,    4: True
                   ,    2: True
                   ,    1: True
                    }
        actual = bitmap(16383)
        self.assertEqual(expected, actual)

    def testHighPlusOne(self):
        self.assertRaises(ValueError, bitmap, 16384)

    def testMixed(self):
        expected = { 8192: False
                   , 4096: False
                   , 2048: False
                   , 1024: False
                   ,  512: False
                   ,  256: False
                   ,  128: False
                   ,   64: False
                   ,   32: False
                   ,   16: True
                   ,    8: False
                   ,    4: True
                   ,    2: False
                   ,    1: True
                    }
        actual = bitmap(21)
        self.assertEqual(expected, actual)

    def testSizeOption(self):
        expected = {   16: True
                   ,    8: False
                   ,    4: True
                   ,    2: False
                   ,    1: True
                    }
        actual = bitmap(21, size=5)
        self.assertEqual(expected, actual)

    def testKeysOption(self):
        expected = { 'foo': True
                   , 'bar': False
                   , 'baz': True
                   , 'buz': False
                   , 'bip': True
                    }
        actual = bitmap(21, size=5, keys=('foo','bar','baz','buz','bip'))
        self.assertEqual(expected, actual)

    def testBucketOption(self):
        expected = Bucket()
        expected.foo = True
        expected.bar = False
        expected.baz = True
        expected.buz = False
        expected.bip = True

        actual = bitmap(21, 5, ('foo','bar','baz','buz','bip'), bucket=True)
        self.assertEqual(expected.__dict__, actual.__dict__)

    def testBucketWrapper(self):
        expected = Bucket()
        expected.foo = True
        expected.bar = False
        expected.baz = True
        expected.buz = False
        expected.bip = True

        actual = bitbucket(21, ('foo','bar','baz','buz','bip'))
        self.assertEqual(expected.__dict__, actual.__dict__)

    def testBucketWrapperMustHaveNames(self):
        self.assertRaises(TypeError, bitbucket, 21)

    def testNMustBeAnInt(self):
        self.assertRaises(TypeError, bitmap, 'foo')

    def testButWeWillCoerceIt(self):
        expected = {1: True}
        actual = bitmap('1', size=1)
        self.assertEqual(expected, actual)

    def testIfWeCan(self):
        self.assertRaises(TypeError, bitmap, None)



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUtilsBitmap))
    return suite

if __name__ == '__main__':
    unittest.main()
