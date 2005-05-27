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
        self.portal.invokeFactory('Folder', 'Docs')
        self.logout()

    def testSomething(self):
        self.login('admin')

        wysiwyg = self.portal.portal_skins.fckeditor_plone.wysiwyg_fckeditor
        expected = 'foo'
        #import pdb; pdb.set_trace()
        actual = wysiwyg('text','')
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
