import unittest
from porter.PorterCmd import PorterCmd

class TestPorter(unittest.TestCase):

    def setUp(self):
        self.c = PorterCmd

    def testOneSingleLetterOpt(self):
        inStr = "-l"
        opts, args = self.c.parse_inStr(inStr)
        self.assertEqual(opts, ['l'])
        self.assertEqual(args, [])

    def testTwoSingleLettersOpts(self):
        inStr = "-la"
        opts, args = self.c.parse_inStr(inStr)
        self.assertEqual(opts, ['l','a'])
        self.assertEqual(args, [])

    def testOneSingleLetterOptAndAWordOpt(self):
        inStr = "-l --long"
        opts, args = self.c.parse_inStr(inStr)
        self.assertEqual(opts, ['l','long'])
        self.assertEqual(args, [])

    def testOneSingleLetterOptAndAWordArg(self):
        inStr = "-l long"
        opts, args = self.c.parse_inStr(inStr)
        self.assertEqual(opts, ['l'])
        self.assertEqual(args, ['long'])

    def testAWordArgAndOneSingleLetterOpt(self):
        inStr = "long -l"
        opts, args = self.c.parse_inStr(inStr)
        self.assertEqual(opts, ['l'])
        self.assertEqual(args, ['long'])

"""
    ['zetaweb.com'
                      ,'thedwarf.com'
                       ,'malcontents.org'
                       ,'jewelryjohn.com'
                       ,'tesm.edu'
"""

if __name__ == '__main__':
    unittest.main()