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

# us
from Products.FCKeditor.tests import FCKPloneTestCase, dict2tuple as d2t


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

        expected = {'folders': []}
        actual = self.fckc.GetFolders(Type, CurrentFolder, User)
        self.assertEqual(d2t(expected), d2t(actual))

        # but only KeyErrors are caught
        CurrentFolder = []
        self.assertRaises(TypeError, self.fckc.GetFolders, Type, CurrentFolder, User)

    # the rest assume the folder exists


    def testUserDoesntHavePermission(self):
        # Member does not have 'List folder contents' on root by default
        # see below
        Type = ''
        CurrentFolder = '/'
        User = self.portal.acl_users.getUser('user')

        expected = {'folders': []}
        actual = self.fckc.GetFolders(Type, CurrentFolder, User)
        self.assertEqual(d2t(expected), d2t(actual))

    def testUserDoesHavePermission(self):
        Type = ''
        CurrentFolder = '/'
        User = self.portal.acl_users.getUser('admin')

        expected = {'folders': ['Docs']}
        actual = self.fckc.GetFolders(Type, CurrentFolder, User)
        self.assertEqual(d2t(expected), d2t(actual))

    def testWorkflowIsHonored(self):
        Type = ''
        CurrentFolder = '/Docs/'
        User = self.portal.acl_users.getUser('user')

        # now you see it...
        expected = {'folders': ['Test']}
        actual = self.fckc.GetFolders(Type, CurrentFolder, User)
        self.assertEqual(d2t(expected), d2t(actual))


        # make Test private
        self.login('admin')
        folder = self.portal.Docs.Test
        pwf = self.portal.portal_workflow
        pwf.doActionFor(folder, 'hide')
        self.logout()

        # prove that Test is now private
        expected = 'private'
        actual = pwf.getInfoFor(folder, 'review_state')
        self.assertEqual(expected, actual)


        # ...now you don't
        expected = {'folders': []}
        actual = self.fckc.GetFolders(Type, CurrentFolder, User)
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
        expected = {'folders': []}
        actual = self.fckc.GetFolders(Type, CurrentFolder, User)
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
        actual = self.fckc.GetFolders(Type, CurrentFolder, User)
        self.assertEqual(d2t(expected), d2t(actual))

    # the rest assume the user has permission on the folder in question


    def testOnlyReturnsFolders(self):
        Type = ''
        CurrentFolder = '/Docs/'
        User = self.portal.acl_users.getUser('user')

        expected = {'folders': ['Test']}
        actual = self.fckc.GetFolders(Type, CurrentFolder, User)
        self.assertEqual(d2t(expected), d2t(actual))

        # add another Folder and an Image for kicks
        self.login('admin')
        self.portal.Docs.invokeFactory('Folder', id='another-folder')
        self.portal.Docs.invokeFactory('Image', id='some-image')
        self.logout()

        expected = {'folders': ['Test', 'another-folder']}
        actual = self.fckc.GetFolders(Type, CurrentFolder, User)
        self.assertEqual(d2t(expected), d2t(actual))


    def testOnlyPermissibleFoldersListed(self):
        Type = ''
        CurrentFolder = '/Docs/'
        User = self.portal.acl_users.getUser('user')

        # now you see it
        expected = {'folders': ['Test']}
        actual = self.fckc.GetFolders(Type, CurrentFolder, User)
        self.assertEqual(d2t(expected), d2t(actual))

        # make the Test folder private so Member's can't see it
        self.login('admin')
        pwf = self.portal.portal_workflow
        pwf.doActionFor(self.portal.Docs.Test, 'hide')
        self.logout()

        # ...now you don't
        expected = {'folders': []}
        actual = self.fckc.GetFolders(Type, CurrentFolder, User)
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
