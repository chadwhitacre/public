import unittest
from porter.PorterCmd import PorterCmd

class TestPorter(unittest.TestCase):

    def setUp(self):
        self.c = PorterCmd

    def testOneSingleLetter(self):
        arg = "-l"
        opts = self.c.parseopts(arg)
        self.assertEqual(opts, ['l'])

    def testTwoSingleLetters(self):
        arg = "-la"
        opts = self.c.parseopts(arg)
        self.assertEqual(opts, ['l','a'])

    def testOneSingleLetterAndAWord(self):
        arg = "-l --long"
        opts = self.c.parseopts(arg)
        self.assertEqual(opts, ['l','long'])

if __name__ == '__main__':
    unittest.main()