# make sure we can find ourselves
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Zope/Plone
from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

# us
from Products.FCKeditor.tests import dict2tuple as d2t
from Products.FCKeditor.PloneFCKmanager import PloneFCKmanager


##
# Tweak the test fixture
##

ZopeTestCase.installProduct('FCKeditor')


##
# Define our tests
##

class Test(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.portal.portal_quickinstaller.installProduct('FCKeditor')
        self.fckm = self.portal.portal_fckmanager

        self.portal.acl_users._doAddUser('admin', 'secret', ['Manager'], [])
        self.portal.acl_users._doAddUser('user', 'secret', ['Member'], [])

        self.login('admin')
        self.portal.invokeFactory('Folder', id='Docs')
        self.portal.Docs.invokeFactory('Folder', id='Test')
        self.portal.Docs.invokeFactory('Document', id='Doc')
        self.portal.Docs.invokeFactory('Image', id='Img')
        self.portal.Docs.invokeFactory('File', id='PDF')
        self.logout()

    def testCurrentFolderDoesntExist(self):
        Type = ''
        CurrentFolder = '/Nonexistant/'
        User = self.portal.acl_users.getUser('admin')

        expected = {'files': [], 'folders': []}
        actual = self.fckm.GetFoldersAndFiles(Type, CurrentFolder, User)
        self.assertEqual(d2t(expected), d2t(actual))

        # but only KeyErrors are caught
        CurrentFolder = []
        self.assertRaises(TypeError, self.fckm.GetFoldersAndFiles, Type, CurrentFolder, User)

    # the rest assume the folder exists


    def testUserDoesntHavePermission(self):
        # Member does not have 'List folder contents' on root by default
        # see below
        Type = ''
        CurrentFolder = '/'
        User = self.portal.acl_users.getUser('user')

        expected = {'files': [], 'folders': []}
        actual = self.fckm.GetFoldersAndFiles(Type, CurrentFolder, User)
        self.assertEqual(d2t(expected), d2t(actual))

    def testUserDoesHavePermission(self):
        Type = ''
        CurrentFolder = '/'
        User = self.portal.acl_users.getUser('admin')

        expected = {'files': [], 'folders': ['Docs']}
        actual = self.fckm.GetFoldersAndFiles(Type, CurrentFolder, User)
        self.assertEqual(d2t(expected), d2t(actual))

    def testWorkflowIsHonored(self):
        Type = ''
        CurrentFolder = '/Docs/'
        User = self.portal.acl_users.getUser('user')

        # now you see it...
        expected = {'files': [('Doc',0),('PDF',0)], 'folders': ['Test']}
        actual = self.fckm.GetFoldersAndFiles(Type, CurrentFolder, User)
        self.assertEqual(d2t(expected), d2t(actual))


        # make Doc private
        self.login('admin')
        doc = self.portal.Docs.Doc
        pwf = self.portal.portal_workflow
        pwf.doActionFor(doc, 'hide')
        self.logout()

        # prove that Doc is now private
        expected = 'private'
        actual = pwf.getInfoFor(doc, 'review_state')
        self.assertEqual(expected, actual)


        # ...now you don't
        expected = {'files': [('PDF',0)], 'folders': ['Test']}
        actual = self.fckm.GetFoldersAndFiles(Type, CurrentFolder, User)
        self.assertEqual(d2t(expected), d2t(actual))

    def testRootListingForMembers(self):
        Type = ''
        CurrentFolder = '/'
        User = self.portal.acl_users.getUser('user')

        # By default, the Member role doesn't have 'List folder contents'
        # permission on the portal object, and furthermore the portal object
        # is not part of a workflow. This means that Members cannot list the
        # contents in the site root.

        # where is it?
        expected = {'files': [], 'folders': []}
        actual = self.fckm.GetFoldersAndFiles(Type, CurrentFolder, User)
        self.assertEqual(d2t(expected), d2t(actual))

        # The suggested workaround is to give them permission manually.
        self.login('admin')
        self.portal.manage_permission( "List folder contents"
                                     , ('Manager', 'Owner', 'Member')
                                     , acquire=1
                                      )
        self.logout()


        # there it is! NOTE: no /index_html in PloneTestCase
        expected = {'files': [], 'folders': ['Docs']}
        actual = self.fckm.GetFoldersAndFiles(Type, CurrentFolder, User)
        self.assertEqual(d2t(expected), d2t(actual))

    # the rest assume the user has permission on the folder in question


    def testNonImageOnlyReturnsDocsAndFiles(self):
        Type = 'Foo' # can be anything besides 'Image'
        CurrentFolder = '/Docs/'
        User = self.portal.acl_users.getUser('user')

        expected = {'files': [('Doc',0),('PDF',0)], 'folders': ['Test']}
        actual = self.fckm.GetFoldersAndFiles(Type, CurrentFolder, User)
        self.assertEqual(d2t(expected), d2t(actual))

        Type = [] # really, anything

        expected = {'files': [('Doc',0),('PDF',0)], 'folders': ['Test']}
        actual = self.fckm.GetFoldersAndFiles(Type, CurrentFolder, User)
        self.assertEqual(d2t(expected), d2t(actual))


    def testImageOnlyReturnsImages(self):
        Type = 'Image'
        CurrentFolder = '/Docs/'
        User = self.portal.acl_users.getUser('user')

        expected = {'files': [('Img',0)], 'folders': ['Test']}
        actual = self.fckm.GetFoldersAndFiles(Type, CurrentFolder, User)
        self.assertEqual(d2t(expected), d2t(actual))

    def testSize(self):
        content = 'I AM THE CONTENT!!!!!!!!' * 50 # needs to be bigger than a KB
        self.portal.Docs.Doc.edit('text/html', content)
        #get_transaction().commit()

        # actual size is given in bytes
        expected = 1718
        actual = self.portal.Docs.Doc.get_size()
        self.assertEqual(expected, actual)

        Type = ''
        CurrentFolder = '/Docs/'
        User = self.portal.acl_users.getUser('user')

        # but we want size rounded to nearest kilobyte
        expected = {'files': [('Doc',2),('PDF',0)], 'folders': ['Test']}
        actual = self.fckm.GetFoldersAndFiles(Type, CurrentFolder, User)
        self.assertEqual(d2t(expected), d2t(actual))




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
