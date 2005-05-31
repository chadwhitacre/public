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
        NewFolderName = 'Foo'

        expected = {'error_code': 110}
        actual = self.fckc.CreateFolder(Type, CurrentFolder, NewFolderName)
        self.assertEqual(d2t(expected), d2t(actual))

        # but only KeyErrors are caught
        CurrentFolder = []
        self.assertRaises( TypeError, self.fckc.CreateFolder, Type
                         , CurrentFolder, NewFolderName
                          )

    # the rest assume the folder exists


    def testUserDoesntHavePermission(self):
        Type = ''
        CurrentFolder = '/'
        NewFolderName = 'Foo'

        expected = {'error_code': 103}
        self.login('user')
        actual = self.fckc.CreateFolder(Type, CurrentFolder, NewFolderName)
        self.logout()
        self.assertEqual(d2t(expected), d2t(actual))

    def testUserDoesHavePermission(self):
        Type = ''
        CurrentFolder = '/'
        NewFolderName = 'Foo'

        expected = {'error_code': 0}
        self.login('admin')
        actual = self.fckc.CreateFolder(Type, CurrentFolder, NewFolderName)
        self.logout()
        self.assertEqual(d2t(expected), d2t(actual))

    # the rest assume the user has permission on the folder in question


    def testNameCollision(self):
        Type = ''
        CurrentFolder = '/'
        NewFolderName = 'Docs'

        expected = {'error_code': 101}
        self.login('admin')
        actual = self.fckc.CreateFolder(Type, CurrentFolder, NewFolderName)
        self.logout()
        self.assertEqual(d2t(expected), d2t(actual))

    def testPloneCheckId(self):
        Type = ''
        CurrentFolder = '/'
        NewFolderName = ''

        def createFolder(NewFolderName):
            self.login('admin')
            return self.fckc.CreateFolder(Type, CurrentFolder, NewFolderName)
            self.logout()

        # in 2.0.5 check_id catches bad Zope id's (among other things)
        expected = {'error_code': 102}
        actual = createFolder('!!!!foofoofoof!!!!!')
        self.assertEqual(d2t(expected), d2t(actual))

        # but it does not enforce name collisions induced by portal_skins,
        # which means we can override check_id, e.g.
        expected = {'error_code': 0}
        actual = createFolder('check_id')
        self.assertEqual(d2t(expected), d2t(actual))

        # then next time we add something we will get strange behavior
        self.assertRaises(TypeError, createFolder, 'IShouldWork')

        # (clean up our mess)
        self.portal.manage_delObjects('check_id')

        # (now it should work again)
        expected = {'error_code': 0}
        actual = createFolder('IShouldWork')
        self.assertEqual(d2t(expected), d2t(actual))

        # edge errors get caught by our catch-all
        expected = {'error_code': 110}
        actual = createFolder([])
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
