#!/usr/bin/env python

import unittest

from citlib.utils import bitmap, Bucket, bitbucket


bitmap_32 = {
    2147483648L: False
  ,  1073741824: False
  ,   536870912: False
  ,   268435456: False
  ,   134217728: False
  ,    67108864: False
  ,    33554432: False
  ,    16777216: False
  ,     8388608: False
  ,     4194304: False
  ,     2097152: False
  ,     1048576: False
  ,      524288: False
  ,      262144: False
  ,      131072: False
  ,       65536: False
  ,       32768: False
  ,       16384: False
  ,        8192: False
  ,        4096: False
  ,        2048: False
  ,        1024: False
  ,         512: False
  ,         256: False
  ,         128: False
  ,          64: False
  ,          32: False
  ,          16: False
  ,           8: False
  ,           4: False
  ,           2: False
  ,           1: False
               }

class TestUtilsBitmap(unittest.TestCase):

    def testBasic(self):
        expected = bitmap_32.copy()
        expected[1] = True
        actual = bitmap(1)
        self.assertEqual(expected, actual)

    def testLow(self):
        expected = bitmap_32.copy()
        actual = bitmap(0)
        self.assertEqual(expected, actual)

    def testLowMinusOne(self):
        self.assertRaises(ValueError, bitmap, -1)

    def testHigh(self):
        expected = bitmap_32.copy()
        for i in expected:
            expected[i] = True
        actual = bitmap(4294967295L)
        self.assertEqual(expected, actual)

    def testHighPlusOne(self):
        self.assertRaises(ValueError, bitmap, 4294967297L)

    def testMixed(self):
        expected = bitmap_32.copy()
        expected[16] = True
        expected[8] = False
        expected[4] = True
        expected[2] = False
        expected[1] = True
        actual = bitmap(21)
        self.assertEqual(expected, actual)

    def testKeysOption(self):
        expected = { 'foo': True
                   , 'bar': False
                   , 'baz': True
                   , 'buz': False
                   , 'bip': True
                    }
        actual = bitmap(21, keys=('foo','bar','baz','buz','bip'))
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

    def testBothKeysAndSizeOptionsGood(self):
        expected = { 'foo': True
                   , 'bar': False
                   , 'baz': True
                   , 'buz': False
                   , 'bip': True
                    }
        actual = bitmap(21, size=5, keys=('foo','bar','baz','buz','bip'))
        self.assertEqual(expected, actual)

    def testBothKeysAndSizeOptionsBad(self):
        self.assertRaises( ValueError
                         , bitmap
                         , 21
                         , size=4
                         , keys=('foo','bar','baz','buz','bip')
                          )

    def testBucketOption(self):
        expected = Bucket()
        expected.foo = True
        expected.bar = False
        expected.baz = True
        expected.buz = False
        expected.bip = True

        actual = bitmap(21, ('foo','bar','baz','buz','bip'), 5, bucket=True)
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

    def testOrdering(self):
        expected = { 16: True
                   ,  8: True
                   ,  4: True
                   ,  2: False
                   ,  1: True
                    }
        actual = bitmap(29, size=5)
        self.assertEqual(expected, actual)

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


    def testIfWePassInKeysWeOnlyGetThoseBack(self):
        expected = {'foo':True, 'bar':False}
        actual = bitmap(2, keys=('foo','bar'))
        self.assertEqual(expected, actual)

    def testDuplicateKeysRaisesValueError(self):
        self.assertRaises(ValueError, bitmap, 2, ('foo','bar','foo'))



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUtilsBitmap))
    return suite

if __name__ == '__main__':
    unittest.main()
