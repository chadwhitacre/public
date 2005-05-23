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
        self.logout()

    def testCurrentFolderDoesntExist(self):
        Type = ''
        CurrentFolder = '/Nonexistant/'
        ComputedUrl = ''
        User = self.portal.acl_users.getUser('admin')

        expected = {'folders': []}
        actual = self.fckm.GetFolders(Type, CurrentFolder, ComputedUrl, User)
        self.assertEqual(d2t(expected), d2t(actual))

    # the rest assume the folder exists


    def testUserDoesntHavePermission(self):
        Type = ''
        CurrentFolder = '/'
        ComputedUrl = ''
        User = self.portal.acl_users.getUser('user')

        expected = {'folders': []}
        actual = self.fckm.GetFolders(Type, CurrentFolder, ComputedUrl, User)
        self.assertEqual(d2t(expected), d2t(actual))

    def testUserDoesHavePermission(self):
        Type = ''
        CurrentFolder = '/'
        ComputedUrl = ''
        User = self.portal.acl_users.getUser('admin')

        expected = {'folders': ['Docs']}
        actual = self.fckm.GetFolders(Type, CurrentFolder, ComputedUrl, User)
        self.assertEqual(d2t(expected), d2t(actual))

    def testWorkflowIsHonored(self):
        Type = ''
        CurrentFolder = '/Docs/'
        ComputedUrl = ''
        User = self.portal.acl_users.getUser('user')

        # now you see it...
        expected = {'folders': ['Test']}
        actual = self.fckm.GetFolders(Type, CurrentFolder, ComputedUrl, User)
        self.assertEqual(d2t(expected), d2t(actual))


        # make Docs private
        self.login('admin')
        folder = self.portal.Docs.Test
        pwf = self.portal.portal_workflow
        pwf.doActionFor(folder, 'hide')
        self.logout()

        # prove that Docs is now private
        expected = 'private'
        actual = pwf.getInfoFor(folder, 'review_state')
        self.assertEqual(expected, actual)


        # ...now you don't
        expected = {'folders': []}
        actual = self.fckm.GetFolders(Type, CurrentFolder, ComputedUrl, User)
        self.assertEqual(d2t(expected), d2t(actual))

    def testRootListingForMembers(self):
        Type = ''
        CurrentFolder = '/'
        ComputedUrl = ''
        User = self.portal.acl_users.getUser('user')

        # By default, the Member role doesn't have 'List folder contents'
        # permission on the portal object, and furthermore the portal object
        # is not part of a workflow. This means that Members cannot list the
        # contents in the site root.

        # where is it?
        expected = {'folders': []}
        actual = self.fckm.GetFolders(Type, CurrentFolder, ComputedUrl, User)
        self.assertEqual(d2t(expected), d2t(actual))

        # The suggested workaround is to give them permission manually.
        self.login('admin')
        self.portal.manage_permission( "List folder contents"
                                     , ('Manager', 'Owner', 'Member')
                                     , acquire=1
                                      )
        self.logout()


        # there it is!
        expected = {'folders': ['Docs']}
        actual = self.fckm.GetFolders(Type, CurrentFolder, ComputedUrl, User)
        self.assertEqual(d2t(expected), d2t(actual))

    # the rest assume the user has permission on the folder in question


    def testOnlyReturnsFolders(self):
        Type = ''
        CurrentFolder = '/Docs/'
        ComputedUrl = ''
        User = self.portal.acl_users.getUser('user')

        expected = {'folders': ['Test']}
        actual = self.fckm.GetFolders(Type, CurrentFolder, ComputedUrl, User)
        self.assertEqual(d2t(expected), d2t(actual))

        # add another Folder and an Image for kicks
        self.login('admin')
        self.portal.Docs.invokeFactory('Folder', id='another-folder')
        self.portal.Docs.invokeFactory('Image', id='some-image')
        self.logout()

        expected = {'folders': ['Test', 'another-folder']}
        actual = self.fckm.GetFolders(Type, CurrentFolder, ComputedUrl, User)
        self.assertEqual(d2t(expected), d2t(actual))


    def testOnlyPermissibleFoldersListed(self):
        Type = ''
        CurrentFolder = '/Docs/'
        ComputedUrl = ''
        User = self.portal.acl_users.getUser('user')

        # now you see it
        expected = {'folders': ['Test']}
        actual = self.fckm.GetFolders(Type, CurrentFolder, ComputedUrl, User)
        self.assertEqual(d2t(expected), d2t(actual))

        # make the Test folder private so Member's can't see it
        self.login('admin')
        pwf = self.portal.portal_workflow
        pwf.doActionFor(self.portal.Docs.Test, 'hide')
        self.logout()

        # ...now you see don't
        expected = {'folders': []}
        actual = self.fckm.GetFolders(Type, CurrentFolder, ComputedUrl, User)
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
