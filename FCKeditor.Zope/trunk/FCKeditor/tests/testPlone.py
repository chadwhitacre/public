import os, sys, time
from pprint import pprint
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))


##
# Tweak the test fixture
##

from Testing import ZopeTestCase
try:
    from Products.CMFPlone.tests import PloneTestCase

    ZopeTestCase.installProduct('FCKeditor')


    ##
    # Define our tests
    ##

    # I thought we needed this but now I think we don't; keeping it around in case
    #  we do
    #
    #from Products.ExternalMethod import ExternalMethod
    #class TestFCKeditorQuickinstaller(PloneTestCase.PloneTestCase):
    #    """QI swallows exceptions, so before relying on it for the other tests we
    #    try out the install script as an ExternalMethod.
    #    """
    #
    #    def afterSetUp(self):
    #        InstallMethod = ExternalMethod( id = 'InstallTester'
    #                                      , title = ''
    #                                      , module = 'FCKeditor.Install'
    #                                      , function = 'install'
    #                                      )
    #        self.portal._setObject( 'InstallTester', InstallMethod)
    #        self.portal.InstallTester()


    class TestFCKeditorPlone(PloneTestCase.PloneTestCase):

        def afterSetUp(self):
            self.portal.portal_quickinstaller.installProduct('FCKeditor')

        def testInstallation(self):
            self.portal.portal_quickinstaller.isProductInstalled('FCKeditor')

        def testSkins(self):
            self.failUnless( hasattr(self.portal.portal_skins, 'fckeditor_base'),
                             'Missing skin: fckeditor_base')
            self.failUnless( hasattr(self.portal.portal_skins, 'fckeditor_cps'),
                             'Missing skin: fckeditor_cps')
            self.failUnless( hasattr(self.portal.portal_skins, 'fckeditor_plone'),
                             'Missing skin: fckeditor_plone')



    ##
    # Assemble into a suite
    ##



    def test_suite():
        from unittest import TestSuite, makeSuite
        suite = TestSuite()
        suite.addTest(makeSuite(TestFCKeditorPlone))
        return suite

    if __name__ == '__main__':
        framework()

except ImportError:
    print 'PloneTestCase not found.'


