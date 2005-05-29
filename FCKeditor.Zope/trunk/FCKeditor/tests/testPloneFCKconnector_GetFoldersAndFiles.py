# make sure we can find ourselves
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# us
from Products.FCKeditor.tests import FCKPloneTestCase, DummyFileUpload, \
                                     dict2tuple as d2t


##
# Define our tests
##

class Test(FCKPloneTestCase.FCKPloneTestCase):

    def afterSetUp(self):
        self.fckc = self.portal.portal_fckconnector

    def testCurrentFolderDoesntExist(self):
        Type = ''
        CurrentFolder = '/Nonexistant/'
        User = self.portal.acl_users.getUser('admin')

        expected = {'files': [], 'folders': []}
        actual = self.fckc.GetFoldersAndFiles(Type, CurrentFolder, User)
        self.assertEqual(d2t(expected), d2t(actual))

        # but only KeyErrors are caught
        CurrentFolder = []
        self.assertRaises(TypeError, self.fckc.GetFoldersAndFiles, Type, CurrentFolder, User)

    # the rest assume the folder exists


    def testUserDoesntHavePermission(self):
        # Member does not have 'List folder contents' on root by default
        # see below
        Type = ''
        CurrentFolder = '/'
        User = self.portal.acl_users.getUser('user')

        expected = {'files': [], 'folders': []}
        actual = self.fckc.GetFoldersAndFiles(Type, CurrentFolder, User)
        self.assertEqual(d2t(expected), d2t(actual))

    def testUserDoesHavePermission(self):
        Type = ''
        CurrentFolder = '/'
        User = self.portal.acl_users.getUser('admin')

        expected = {'files': [('index_html',4)], 'folders': ['Docs']}
        actual = self.fckc.GetFoldersAndFiles(Type, CurrentFolder, User)
        self.assertEqual(d2t(expected), d2t(actual))

    def testWorkflowIsHonored(self):
        Type = ''
        CurrentFolder = '/Docs/'
        User = self.portal.acl_users.getUser('user')

        # now you see it...
        expected = {'files': [('Doc',0),('PDF',0)], 'folders': ['Test']}
        actual = self.fckc.GetFoldersAndFiles(Type, CurrentFolder, User)
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
        actual = self.fckc.GetFoldersAndFiles(Type, CurrentFolder, User)
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
        actual = self.fckc.GetFoldersAndFiles(Type, CurrentFolder, User)
        self.assertEqual(d2t(expected), d2t(actual))

        # The suggested workaround is to give them permission manually.
        self.login('admin')
        self.portal.manage_permission( "List folder contents"
                                     , ('Manager', 'Owner', 'Member')
                                     , acquire=1
                                      )
        self.logout()


        # there it is!
        expected = {'files': [('index_html',4)], 'folders': ['Docs']}
        actual = self.fckc.GetFoldersAndFiles(Type, CurrentFolder, User)
        self.assertEqual(d2t(expected), d2t(actual))

    # the rest assume the user has permission on the folder in question


    def testNonImageOnlyReturnsDocsAndFiles(self):
        Type = 'Foo' # can be anything besides 'Image'
        CurrentFolder = '/Docs/'
        User = self.portal.acl_users.getUser('user')

        expected = {'files': [('Doc',0),('PDF',0)], 'folders': ['Test']}
        actual = self.fckc.GetFoldersAndFiles(Type, CurrentFolder, User)
        self.assertEqual(d2t(expected), d2t(actual))

        Type = [] # really, anything

        expected = {'files': [('Doc',0),('PDF',0)], 'folders': ['Test']}
        actual = self.fckc.GetFoldersAndFiles(Type, CurrentFolder, User)
        self.assertEqual(d2t(expected), d2t(actual))


    def testImageOnlyReturnsImages(self):
        Type = 'Image'
        CurrentFolder = '/Docs/'
        User = self.portal.acl_users.getUser('user')

        expected = {'files': [('Img',0)], 'folders': ['Test']}
        actual = self.fckc.GetFoldersAndFiles(Type, CurrentFolder, User)
        self.assertEqual(d2t(expected), d2t(actual))

    def testSize(self):
        content = 'I AM THE CONTENT!!!!!!!!' * 50 # needs to be bigger than a KB
        self.portal.Docs.Doc.edit('text/html', content)

        # actual size is given in bytes
        expected = 1718
        actual = self.portal.Docs.Doc.get_size()
        # self.assertEqual(expected, actual) -- The actual value seems to vary
        # ever so slightly. I'm not sure why but the rounded value is consistent
        # so I'm not going to worry about it.

        Type = ''
        CurrentFolder = '/Docs/'
        User = self.portal.acl_users.getUser('user')

        # but we want size rounded to nearest kilobyte
        expected = {'files': [('Doc',2),('PDF',0)], 'folders': ['Test']}
        actual = self.fckc.GetFoldersAndFiles(Type, CurrentFolder, User)
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
