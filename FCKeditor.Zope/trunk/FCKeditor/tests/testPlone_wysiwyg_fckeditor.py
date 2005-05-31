#BOILERPLATE###################################################################
#                                                                             #
#  This package wraps FCKeditor for use in the Zope web application server.   #
#  Copyright (C) 2005 Chad Whitacre <http://www.zetadev.com/>                 #
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
###################################################################BOILERPLATE#
# make sure we can find ourselves
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Zope/Plone
from AccessControl import getSecurityManager

# us
from Products.FCKeditor.tests import FCKPloneTestCase

##
# Define our tests
##

class TestData:

    COMPATIBLE_BASIC = """\
<div>
    <input type="hidden"
           id="text"
           name="text"
           value="" />
    <input type="hidden"
           id="text___Config"
           value="CustomConfigurationsPath=%2Ffckcustom.js" />
    <iframe id="text___Frame"
            src="/FCKeditor/editor/fckeditor.html?InstanceName=text&Toolbar=Basic"
            width="100%" height="500px"
            frameborder="no" scrolling="no"
            tabindex="0"></iframe>
</div>"""

    COMPATIBLE = COMPATIBLE_BASIC

    COMPATIBLE_DEFAULT = """\
<div>
    <input type="hidden"
           id="text"
           name="text"
           value="" />
    <input type="hidden"
           id="text___Config"
           value="CustomConfigurationsPath=%2Ffckcustom.js" />
    <iframe id="text___Frame"
            src="/FCKeditor/editor/fckeditor.html?InstanceName=text&Toolbar=Default"
            width="100%" height="500px"
            frameborder="no" scrolling="no"
            tabindex="0"></iframe>
</div>"""

    INCOMPATIBLE = """\
<div>
    <textarea name="text"
              rows="4" cols="40"
              style="width: 100%; height: 500px;"
              wrap="virtual"
              tabindex="0">
        """+"""
    </textarea>
</div>"""




    STX = """\
<div>
    <input type="hidden"
           id="text"
           name="text"
           value="&lt;h3&gt;Yar yar.&lt;/h3&gt;\n&lt;p&gt; yar yar.&lt;/p&gt;
" />
    <input type="hidden"
           id="text___Config"
           value="CustomConfigurationsPath=%2Ffckcustom.js" />
    <iframe id="text___Frame"
            src="/FCKeditor/editor/fckeditor.html?InstanceName=text&Toolbar=Basic"
            width="100%" height="500px"
            frameborder="no" scrolling="no"
            tabindex="0"></iframe>
</div>"""


    PLAIN = """\
<div>
    <input type="hidden"
           id="text"
           name="text"
           value="Yar yar.&lt;br /&gt;\n&lt;br /&gt;\n yar yar." />
    <input type="hidden"
           id="text___Config"
           value="CustomConfigurationsPath=%2Ffckcustom.js" />
    <iframe id="text___Frame"
            src="/FCKeditor/editor/fckeditor.html?InstanceName=text&Toolbar=Basic"
            width="100%" height="500px"
            frameborder="no" scrolling="no"
            tabindex="0"></iframe>
</div>"""

    HTML = """\
<div>
    <input type="hidden"
           id="text"
           name="text"
           value="Yar yar.\n\n yar yar." />
    <input type="hidden"
           id="text___Config"
           value="CustomConfigurationsPath=%2Ffckcustom.js" />
    <iframe id="text___Frame"
            src="/FCKeditor/editor/fckeditor.html?InstanceName=text&Toolbar=Basic"
            width="100%" height="500px"
            frameborder="no" scrolling="no"
            tabindex="0"></iframe>
</div>"""

class Test(FCKPloneTestCase.FCKPloneTestCase):

    def afterSetUp(self):
        self.wysiwyg = self.portal.portal_skins.fckeditor_plone.wysiwyg_fckeditor


    # Everyone has permission.

    def testManagerHasPermission(self):
        self.login('admin')

        # prove we are a Manager
        expected = True
        actual = getSecurityManager().getUser().has_role('Manager')
        self.assertEqual(expected, actual)

        try:
            self.wysiwyg('text','')
        except Unauthorized:
            self.fail("Manager should have permission but doesn't")

        self.logout()

    def testMemberHasPermission(self):
        self.login('user')

        # prove we are a Member
        expected = True
        actual = getSecurityManager().getUser().has_role('Member')
        self.assertEqual(expected, actual)

        try:
            self.wysiwyg('text','')
        except Unauthorized:
            self.fail("Member should have permission but doesn't")

        self.logout()

    def testAnonymousHasPermission(self):
        self.logout()

        # prove we are Anonymous
        expected = True
        actual = getSecurityManager().getUser().has_role('Anonymous')
        self.assertEqual(expected, actual)

        try:
            self.wysiwyg('text','')
        except Unauthorized:
            self.fail("Anonymous should have permission but doesn't")


    # Different browsers get different widgets.

    def testCompatibleBrowser(self):
        self.app.REQUEST['HTTP_USER_AGENT'] =\
            'Mozilla/5.0 (X11; U; Linux i586; en-US; rv:1.3) Gecko/20030313'
        expected = TestData.COMPATIBLE
        actual = self.wysiwyg('text','')
        self.assertEqual(expected, actual)

    def testIncompatibleBrowser(self):
        self.app.REQUEST['HTTP_USER_AGENT'] =\
            'Mozilla/4.0 (compatible; MSIE 5.01; Windows 95; QXW0332b)'
        expected = TestData.INCOMPATIBLE
        actual = self.wysiwyg('text','')
        self.assertEqual(expected, actual)


    # Different roles get different toolbars.

    def testManagerToolbar(self):
        self.app.REQUEST['HTTP_USER_AGENT'] =\
            'Mozilla/5.0 (X11; U; Linux i586; en-US; rv:1.3) Gecko/20030313'

        self.login('admin')
        expected = TestData.COMPATIBLE_DEFAULT
        actual = self.wysiwyg('text','')
        self.assertEqual(expected, actual)
        self.logout()

    def testMemberToolbar(self):
        self.app.REQUEST['HTTP_USER_AGENT'] =\
            'Mozilla/5.0 (X11; U; Linux i586; en-US; rv:1.3) Gecko/20030313'

        self.login('user')
        expected = TestData.COMPATIBLE_BASIC
        actual = self.wysiwyg('text','')
        self.assertEqual(expected, actual)
        self.logout()

    def testAnonymousToolbar(self):
        self.app.REQUEST['HTTP_USER_AGENT'] =\
            'Mozilla/5.0 (X11; U; Linux i586; en-US; rv:1.3) Gecko/20030313'

        expected = TestData.COMPATIBLE_BASIC
        actual = self.wysiwyg('text','')
        self.assertEqual(expected, actual)


    # Data should be transformed and escaped.

    def testSTX(self):
        self.app.REQUEST['HTTP_USER_AGENT'] =\
            'Mozilla/5.0 (X11; U; Linux i586; en-US; rv:1.3) Gecko/20030313'

        self.login('admin')
        self.portal.Docs.Test.invokeFactory( 'Document'
                                           , 'Doc'
                                           , text='Yar yar.\n\n yar yar.'
                                            )
        self.logout()

        context = self.portal.restrictedTraverse('Docs/Test/Doc')

        # structured text is the default
        expected = 'structured-text'
        actual = context.text_format
        self.assertEqual(expected, actual)

        wysiwyg = self.portal.restrictedTraverse('Docs/Test/Doc/wysiwyg_fckeditor')
        expected = TestData.STX
        actual = wysiwyg('text',context.text)
        self.assertEqual(expected, actual)

    def testPlain(self):
        self.app.REQUEST['HTTP_USER_AGENT'] =\
            'Mozilla/5.0 (X11; U; Linux i586; en-US; rv:1.3) Gecko/20030313'

        self.login('admin')
        self.portal.Docs.Test.invokeFactory( 'Document'
                                           , 'Doc'
                                           , text='Yar yar.\n\n yar yar.'
                                            )
        self.logout()

        context = self.portal.restrictedTraverse('Docs/Test/Doc')

        # change text_format to plain
        context.text_format = 'plain'

        wysiwyg = self.portal.restrictedTraverse('Docs/Test/Doc/wysiwyg_fckeditor')
        expected = TestData.PLAIN
        actual = wysiwyg('text',context.text)
        self.assertEqual(expected, actual)

    def testHTML(self):
        self.app.REQUEST['HTTP_USER_AGENT'] =\
            'Mozilla/5.0 (X11; U; Linux i586; en-US; rv:1.3) Gecko/20030313'

        self.login('admin')
        self.portal.Docs.Test.invokeFactory( 'Document'
                                           , 'Doc'
                                           , text='Yar yar.\n\n yar yar.'
                                            )
        self.logout()

        context = self.portal.restrictedTraverse('Docs/Test/Doc')

        # change text_format to html
        context.text_format = 'html'

        wysiwyg = self.portal.restrictedTraverse('Docs/Test/Doc/wysiwyg_fckeditor')
        expected = TestData.HTML
        actual = wysiwyg('text',context.text)
        self.assertEqual(expected, actual)


##
# Assemble into a suite and run
##

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(Test))
    return suite

if __name__ == '__main__':
    framework()
