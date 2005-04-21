"""Zope-specific tests
"""

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

ZopeTestCase.installProduct('FCKeditor')


from Products.FCKeditor.ZopeFCKeditor import ZopeFCKeditor

class TestSomeProduct(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        factory = self.folder.manage_addProduct['FCKeditor']
        factory.manage_addFCKeditor('fckeditor', None)


    def testSomething(self):
        self.failUnless(hasattr(self.folder, 'fckeditor'),
                        "FCKeditor was not installed")
        self.failUnless(isinstance(self.folder.fckeditor, ZopeFCKeditor),
                        "FCKeditor was not installed properly")


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSomeProduct))
    return suite

if __name__ == '__main__':
    framework()

