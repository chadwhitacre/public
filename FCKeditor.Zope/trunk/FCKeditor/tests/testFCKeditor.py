#BOILERPLATE###################################################################
#                                                                             #
#  This package wraps FCKeditor for use in the Zope web application server.   #
#  Copyright (C) 2005 Chad Whitacre < http://www.zetadev.com/ >               #
#                                                                             #
#  This library is free software; you can redistribute it and/or modify it    #
#  under the terms of the GNU Lesser General Public License as published by   #
#  the Free Software Foundation; either version 2.1 of the License, or (at    #
#  your option) any later version.                                            #
#                                                                             #
#  This library is distributed in the hope that it will be useful, but        #
#  WITHOUT ANY WARRANTY; without even the implied warranty of                 #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser    #
#  General Public License for more details.                                   #
#                                                                             #
#  You should have received a copy of the GNU Lesser General Public License   #
#  along with this library; if not, write to the Free Software Foundation,    #
#  Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA                #
#                                                                             #
#                                                                             #
###################################################################BOILERPLATE#
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


    # _scrub

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

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(Test))
    return suite

if __name__ == '__main__':
    unittest.main()
