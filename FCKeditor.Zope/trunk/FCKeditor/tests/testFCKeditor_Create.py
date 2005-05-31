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

    DEFAULT_COMPATIBLE = """\
<div>
    <input type="hidden"
           id="MyEditor"
           name="MyEditor"
           value="" />
    <input type="hidden"
           id="MyEditor___Config"
           value="" />
    <iframe id="MyEditor___Frame"
            src="/FCKeditor/editor/fckeditor.html?InstanceName=MyEditor&Toolbar=Default"
            width="100%" height="200px"
            frameborder="no" scrolling="no"></iframe>
</div>"""

    DEFAULT_INCOMPATIBLE = """\
<div>
    <textarea name="MyEditor"
              rows="4" cols="40"
              style="width: 100%; height: 200px;"
              wrap="virtual">
        """+"""
    </textarea>
</div>"""

    VALUE = """\
<html>
<head>
    <title>TEST</title>
</head>
<body>
    Foo.
</body>
</html>
        """

    REPLACED_COMPATIBLE = """\
<div>
    <input type="hidden"
           id="CustomEditor"
           name="CustomEditor"
           value="&lt;html&gt;
&lt;head&gt;
    &lt;title&gt;TEST&lt;/title&gt;
&lt;/head&gt;
&lt;body&gt;
    Foo.
&lt;/body&gt;
&lt;/html&gt;
        " />
    <input type="hidden"
           id="CustomEditor___Config"
           value="AutoDetectLanguage=false&DefaultLanguage=pt-BR" />
    <iframe id="CustomEditor___Frame"
            src="/AltPath/editor/fckeditor.html?InstanceName=CustomEditor&Toolbar=CustomToolbar"
            width="80%" height="400px"
            frameborder="no" scrolling="no"></iframe>
</div>"""

    REPLACED_INCOMPATIBLE = """\
<div>
    <textarea name="CustomEditor"
              rows="4" cols="40"
              style="width: 80%; height: 400px;"
              wrap="virtual">
        &lt;html&gt;
&lt;head&gt;
    &lt;title&gt;TEST&lt;/title&gt;
&lt;/head&gt;
&lt;body&gt;
    Foo.
&lt;/body&gt;
&lt;/html&gt;
        """+"""
    </textarea>
</div>"""

class Test(unittest.TestCase):

    def setUp(self):
        self.fck = FCKeditor()

    def testCompatibleMustBeSet(self):
        self.assertRaises(FCKexception, self.fck.Create)

    def testCompatible(self):
        self.fck.Compatible = True
        expected = TestData.DEFAULT_COMPATIBLE
        actual = self.fck.Create()
        self.assertEqual(expected, actual)

    def testIncompatible(self):
        self.fck.Compatible = False
        expected = TestData.DEFAULT_INCOMPATIBLE
        actual = self.fck.Create()
        self.assertEqual(expected, actual)

    def testReplacedCompatible(self):
        self.fck.Config = {'AutoDetectLanguage':'false'
                          ,'DefaultLanguage':'pt-BR'
                           }
        self.fck.InstanceName = 'CustomEditor'
        self.fck.Width = '80%'
        self.fck.Height = 400 # int should be converted to '400px'
        self.fck.ToolbarSet = 'CustomToolbar'
        self.fck.BasePath = '/AltPath/'
        self.fck.Value = TestData.VALUE

        self.fck.Compatible = True
        expected = TestData.REPLACED_COMPATIBLE
        actual = self.fck.Create()
        self.assertEqual(actual, expected)

    def testReplacedIncompatible(self):
        self.fck.Config = {'AutoDetectLanguage':'false'
                          ,'DefaultLanguage':'pt-BR'
                           }
        self.fck.InstanceName = 'CustomEditor'
        self.fck.Width = '80%'
        self.fck.Height = 400 # int should be converted to '400px'
        self.fck.ToolbarSet = 'CustomToolbar'
        self.fck.BasePath = '/AltPath/'
        self.fck.Value = TestData.VALUE

        self.fck.Compatible = False
        expected = TestData.REPLACED_INCOMPATIBLE
        actual = self.fck.Create()
        self.assertEqual(actual, expected)

    # _parse_dimensions

    def testIntsBecomePixels(self):
        w, h =(300, 400)

        expected = ('300px', '400px')
        actual = self.fck._parse_dimensions(w, h)
        self.assertEqual(expected, actual)

    def testStringsAreUnchanged(self):
        w, h =('300px', '400px')

        expected = ('300px', '400px')
        actual = self.fck._parse_dimensions(w, h)
        self.assertEqual(expected, actual)

    def testStringInputCanBeWhatever(self):
        w, h = ('I AM A STRING', "NOI YOU'RE NOT! I AM!!!")

        expected = ('I AM A STRING', "NOI YOU'RE NOT! I AM!!!")
        actual = self.fck._parse_dimensions(w, h)
        self.assertEqual(expected, actual)

    def testIncludingTheEmptyString(self):
        w, h = ('', "")

        expected = ('', "")
        actual = self.fck._parse_dimensions(w, h)
        self.assertEqual(expected, actual)

    def testWeDontDoAnyValidation(self):
        w, h = ('Watch this', list())

        expected = ('Watch this', [])
        actual = self.fck._parse_dimensions(w, h)
        self.assertEqual(expected, actual)


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
