import os
import sys
import unittest

# make sure we can find ourselves
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# the thing we want to test
from Products.FCKeditor import FCKexception
from Products.FCKeditor.FCKeditor import FCKeditor

##
# Define our tests
##

class Test(unittest.TestCase):

    def setUp(self):
        self.fck = FCKeditor()

    def testGoodData(self):
        unscrubbed = "this-is-fine"
        expected = 'this-is-fine'
        actual = self.fck._scrub(unscrubbed)
        self.assertEqual(expected, actual)

    def testBadCharsReplaced(self):
        unscrubbed = "here are some illegal characters: ! ' / @ # ~ % , $ * ."
        expected = 'here-are-some-illegal-characters-----------------------'
        actual = self.fck._scrub(unscrubbed)
        self.assertEqual(expected, actual)

    def testMustStartWithAlpha(self):
        # we are a little stricter than the spec here
        unscrubbed = "123456 <- can't do this"
        expected = 'can-t-do-this'
        actual = self.fck._scrub(unscrubbed)
        self.assertEqual(expected, actual)

    def testButInternalNumbersOK(self):
        unscrubbed = "but this is fine: 123456"
        expected = 'but-this-is-fine--123456'
        actual = self.fck._scrub(unscrubbed)
        self.assertEqual(expected, actual)

    def testSpecAllowsUnderscores(self):
        unscrubbed = "but_not_sure_about_browser_support"
        expected = 'but_not_sure_about_browser_support'
        actual = self.fck._scrub(unscrubbed)
        self.assertEqual(expected, actual)


    # if we don't have at least one good char, we raise an exception

    def testSingleGoodChar(self):
        unscrubbed = "a"
        expected = 'a'
        actual = self.fck._scrub(unscrubbed)
        self.assertEqual(expected, actual)

    def testSingleGoodCharWithBadChars(self):
        unscrubbed = "123456----_____!@#$a"
        expected = 'a'
        actual = self.fck._scrub(unscrubbed)
        self.assertEqual(expected, actual)

    def testEmptyInput(self):
        unscrubbed = ""
        self.assertRaises(FCKexception, self.fck._scrub, unscrubbed)

    def testOnlyBadChars(self):
        unscrubbed = "123: ! ' / @ # ~ % , $ * ."
        self.assertRaises(FCKexception, self.fck._scrub, unscrubbed)

    def testSingleBadChar(self):
        unscrubbed = "!"
        self.assertRaises(FCKexception, self.fck._scrub, unscrubbed)

    def testSingleNonAlphaChar(self):
        unscrubbed = "-"
        self.assertRaises(FCKexception, self.fck._scrub, unscrubbed)



##
# And run them!
##

if __name__ == '__main__':
    unittest.main()
