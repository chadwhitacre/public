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

class TestData:

    # useragent strings randomly grabbed from:
    #
    #    http://www.google.com/search?q=user+agent+string

    COMPATIBLE_USERAGENTS = """\
Mozilla/5.0 (X11; U; Linux i586; en-US; rv:1.3) Gecko/20030313
Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US; rv:1.5a) Gecko/20030718
Mozilla/5.0 (Windows; U; Windows NT 5.1; de-DE; rv:1.5a) Gecko/20030728 Mozilla Firebird/0.6.1
Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.5) Gecko/20031016 K-Meleon/0.8.1
Mozilla/5.0 (X11; U; Linux i686; en-US) Gecko/20031007 Firebird/0.7
Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US; rv:1.6) Gecko/20040210 Firefox/0.8
Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.2) Gecko/20040803 MultiZilla/1.6.4.0b
Mozilla /4.0 (compatible; MSIE 6.0; i686 Linux)
Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; YPC 3.0.3; sbcydsl 3.12; FunWebProducts; Alexa Toolbar)
Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; Rogers Hi-Speed Internet; iebar; .NET CLR 1.1.4322)
Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; Maxthon; FREE; .NET CLR 1.1.4322; .NET CLR 2.0.40607)
Mozilla/4.0 (compatible; MSIE 6.0b; Windows 98; GTelnet1.0)
Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1) Opera 7.23 [es-ES]
Mozilla/5.0 Opera/7.0 (X11; U; Linux i686; de-DE; rv:1.6) Gecko/20040114
Mozilla/4.0 (compatible; MSIE 5.5; AOL 8.0; Windows 98; Win 9x 4.90; .NET CLR 1.1.4322)
Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 4.0; Version 2/5.5 Customised)
Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.0);JTB:104:a95eef30-9f35-4ec0-bc43-66a16a703faf
        """

    INCOMPATIBLE_USERAGENTS = """\
Mozilla/5.0 (X11; U; Linux i686; en-US; rv:0.9.9) Gecko/20020513
Mozilla/5.0 (Windows; U; WinNT4.0; en-US; rv:1.2.1) Gecko/20021130
Mozilla/4.0 (AmigaOS 3.1)
Mozilla/4.0 (compatible; MSIE 5.01; Windows NT 5.0; DigExt; iebar; (R1 1.5))
Mozilla/4.0 (compatible; MSIE 5.0; Mac_PowerPC; S425166QXM03307)
Mozilla/4.0 (compatible; MSIE 5.01; Windows 95; QXW0332b)
Mozilla/4.0 (compatible; MSIE 5.0; Windows 95) Opera 5.12 [en]
Opera/7.11 (Linux 2.4.18-xfs i686; U) [en]
Opera/7.50 (Windows NT 5.2; U) [en]
Opera/8.00 (Windows; U)
Opera/7.54 (FreeBSD; U)
        """

class Test(unittest.TestCase):

    def setUp(self):
        self.fck = FCKeditor()

    def testCompatible(self):
        i = 0
        for useragent in TestData.COMPATIBLE_USERAGENTS.split(os.linesep):
            i += 1
            if useragent.strip():
                self.failUnless(self.fck.SetCompatible(useragent),
                                "compatible failed on #%s: %s" % (i, useragent))

    def testIncompatible(self):
        i = 0
        for useragent in TestData.INCOMPATIBLE_USERAGENTS.split(os.linesep):
            i += 1
            if useragent.strip():
                self.failIf(self.fck.SetCompatible(useragent),
                            "incompatible failed on #%s: %s" % (i, useragent))


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
