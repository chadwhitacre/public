if __name__ == '__main__':
    import framework

import unittest
from Porter.Porter import Porter

class TestParseInStr(unittest.TestCase):

    def setUp(self):
        self.c = Porter

    def testOneSingleLetterOpt(self):
        inStr = "-l"
        opts, args = self.c._parse_inStr(inStr)
        self.assertEqual(opts, ['l'])
        self.assertEqual(args, [])

    def testTwoSingleLettersOpts(self):
        inStr = "-la"
        opts, args = self.c._parse_inStr(inStr)
        self.assertEqual(opts, ['l','a'])
        self.assertEqual(args, [])

    def testOneSingleLetterOptAndAWordOpt(self):
        inStr = "-l --long"
        opts, args = self.c._parse_inStr(inStr)
        self.assertEqual(opts, ['l','long'])
        self.assertEqual(args, [])

    def testOneSingleLetterOptAndAWordArg(self):
        inStr = "-l long"
        opts, args = self.c._parse_inStr(inStr)
        self.assertEqual(opts, ['l'])
        self.assertEqual(args, ['long'])

    def testAWordArgAndOneSingleLetterOpt(self):
        inStr = "long -l"
        opts, args = self.c._parse_inStr(inStr)
        self.assertEqual(opts, ['l'])
        self.assertEqual(args, ['long'])

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestParseInStr))
    return suite

if __name__ == '__main__':
    unittest.main()