"""Zope-specific tests; requires ZopeTestCase
"""

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.FCKeditor.tests import FCKploneTestCase
from Products.FCKeditor.PloneFCKmanager import PloneFCKmanager

from Products.CMFPlone.PloneUtilities import _createObjectByType

#from AccessControl import Unauthorized
#from zExceptions import BadRequest
#from Products.FCKeditor.ZopeFCKeditor import ZopeFCKeditor
#from data import testdata


##
# stub classes
##

class RESPONSE:
    def setHeader(self, *arg, **kw):
        pass

class AUTHENTICATED_USER:
    def has_permission(self, *arg, **kw):
        return True

from types import DictType
class REQUEST(DictType):
    RESPONSE = RESPONSE()


##
# tests
##

class TestIt(FCKploneTestCase.FCKploneTestCase):

    def afterSetUp(self):
        pass

    def testCurrentFolderDoesntExist(self):
        _createObjectByType(type_name='Folder', container=self.portal, id='path')
        pass
        # nevermind, we assume incoming data is clean
    # the rest assume the folder exists

    def testUserDoesntHavePermission(self):

        data = {}
        data['Type'] = 'Image'
        data['CurrentFolder'] = '/Docs/Test/'
        data['ComputedUrl'] = '/Docs/Test/'
        data['User'] = self.folder.acl_users.getUser('user1')

        self.fckm.GetFolders()

    # the rest assume the user has permission on the folder in question

#    def testObjectValuesOnlyReturnsFolders(self):
#        pass
#
#    def testOnlyPermissibleFoldersListed(self):
#        pass
#
#    def testZeroFoldersToList(self):
#        pass
#
#    def testOneFolderToList(self):
#        pass
#
#    def testThreeFoldersToList(self):
#        pass



##
# Assemble into a suite and run
##

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestIt))
    return suite

if __name__ == '__main__':
    framework()
