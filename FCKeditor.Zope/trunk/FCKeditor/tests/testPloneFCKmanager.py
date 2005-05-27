import os
import sys
import time

# make sure we can find ourselves
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# the thing we want to test
from Products.FCKeditor.PloneFCKmanager import PloneFCKmanager


##
# Tweak the test fixture
##

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

ZopeTestCase.installProduct('FCKeditor')


##
# Define our tests
##

class Test(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.portal.portal_quickinstaller.installProduct('FCKeditor')

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
