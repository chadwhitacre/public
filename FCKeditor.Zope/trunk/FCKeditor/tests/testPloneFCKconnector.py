# make sure we can find ourselves
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Zope/Plone
from AccessControl import getSecurityManager
from Products.FCKeditor.PloneFCKconnector import PloneFCKconnector
from Products.FCKeditor.tests.testPloneFCKconnector_FileUpload import \
                                                                DummyFileUpload


##
# Tweak the test fixture
##

from Testing import ZopeTestCase
from Products.FCKeditor.tests import FCKPloneTestCase


##
# Define our tests
##

class TestData:

    GetFolders = """\
<?xml version="1.0" encoding="utf-8" ?>
  <Connector command="GetFolders" resourceType="File">
    <CurrentFolder path="/" url="/" />
    <Folders>
      <Folder name="Docs" />
    </Folders>
</Connector>"""

    GetFoldersAndFiles = """\
<?xml version="1.0" encoding="utf-8" ?>
  <Connector command="GetFoldersAndFiles" resourceType="File">
    <CurrentFolder path="/" url="/" />
    <Folders>
      <Folder name="Docs" />
    </Folders>
    <Files>
      <File name="index_html" size="4" />
    </Files>
</Connector>"""

    CreateFolder = """\
<?xml version="1.0" encoding="utf-8" ?>
  <Connector command="CreateFolder" resourceType="File">
    <CurrentFolder path="/" url="/" />
    <Error number="0" />
</Connector>"""

    FileUpload = """\
<script type="text/javascript">
    window.parent.frames['frmUpload'].OnUploadCompleted(0) ;
</script>"""


class Test(FCKPloneTestCase.FCKPloneTestCase):

    def testInstallation(self):
        expected = True
        actual = self.portal.portal_quickinstaller.isProductInstalled('FCKeditor')
        self.assertEqual(expected, actual)

    def testSkins(self):
        self.failUnless( hasattr(self.portal.portal_skins, 'fckeditor_base'),
                         'Missing skin: fckeditor_base')
        self.failUnless( hasattr(self.portal.portal_skins, 'fckeditor_plone'),
                         'Missing skin: fckeditor_plone')

    def testLayout(self):
        expected = True
        actual = isinstance(self.portal.portal_fckconnector, PloneFCKconnector)
        self.assertEqual(expected, actual)


    # Make sure we can get to each command TTW; full exercises for each command
    # are in testPloneFCKconnector_*.py

    def testGetFoldersTTW(self):
        self.login('admin')

        self.app.REQUEST.form['Command'] = 'GetFolders'
        self.app.REQUEST.form['Type'] = 'File'
        self.app.REQUEST.form['CurrentFolder'] = '/'
        self.app.REQUEST['AUTHENTICATED_USER'] = getSecurityManager().getUser()

        fckc = self.portal.restrictedTraverse('portal_fckconnector')

        expected = TestData.GetFolders
        actual = fckc(self.app.REQUEST)
        self.assertEqual(expected, actual)

        self.logout()

    def testGetFoldersAndFilesTTW(self):
        self.login('admin')

        self.app.REQUEST.form['Command'] = 'GetFoldersAndFiles'
        self.app.REQUEST.form['Type'] = 'File'
        self.app.REQUEST.form['CurrentFolder'] = '/'
        self.app.REQUEST['AUTHENTICATED_USER'] = getSecurityManager().getUser()

        fckc = self.portal.restrictedTraverse('portal_fckconnector')

        expected = TestData.GetFoldersAndFiles
        actual = fckc(self.app.REQUEST)
        self.assertEqual(expected, actual)

        self.logout()

    def testCreateFolderTTW(self):
        self.login('admin')

        self.app.REQUEST.form['Command'] = 'CreateFolder'
        self.app.REQUEST.form['Type'] = 'File'
        self.app.REQUEST.form['CurrentFolder'] = '/'
        self.app.REQUEST.form['NewFolderName'] = 'foo'
        self.app.REQUEST['AUTHENTICATED_USER'] = getSecurityManager().getUser()

        fckc = self.portal.restrictedTraverse('portal_fckconnector')

        expected = TestData.CreateFolder
        actual = fckc(self.app.REQUEST)
        self.assertEqual(expected, actual)

        # make sure it actually created the folder
        expected = True
        actual = 'foo' in self.portal.objectIds()
        self.assertEqual(expected, actual)

        self.logout()

    def testFileUploadTTW(self):
        self.login('admin')

        self.app.REQUEST.form['Command'] = 'FileUpload'
        self.app.REQUEST.form['Type'] = 'File'
        self.app.REQUEST.form['CurrentFolder'] = '/'
        self.app.REQUEST.form['NewFile'] = DummyFileUpload('blank.pdf')
        self.app.REQUEST['AUTHENTICATED_USER'] = getSecurityManager().getUser()

        fckc = self.portal.restrictedTraverse('portal_fckconnector')

        expected = TestData.FileUpload
        actual = fckc(self.app.REQUEST)
        self.assertEqual(expected, actual)

        # make sure it actually created the file
        expected = True
        actual = 'blank.pdf' in self.portal.objectIds()
        self.assertEqual(expected, actual)

        self.logout()

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
