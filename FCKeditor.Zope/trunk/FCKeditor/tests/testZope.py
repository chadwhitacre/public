"""Zope-specific tests; requires ZopeTestCase
"""

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
ZopeTestCase.installProduct('FCKeditor')

from zExceptions import BadRequest
from Products.FCKeditor.ZopeFCKeditor import ZopeFCKeditor

class TestZopeFCKeditor(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        self.add = self.folder.manage_addProduct['FCKeditor'].manage_addFCKeditor
        self.add('fck')
        self.fck = self.folder.fck

    def testSomething(self):
        self.failUnless(hasattr(self, 'fck'),
                        "FCKeditor was not installed")
        self.failUnless(isinstance(self.fck, ZopeFCKeditor),
                        "FCKeditor was not installed properly")

    def testInstanceNameScrubber(self):
        self.assertEqual(self.fck.InstanceName, 'fck')

        # Zope does do some ID validation -- [^a-zA-Z0-9-_~,.$\(\)# ]
        self.assertRaises( BadRequest, self.add
                         , "123456fck2_oh yeah, believe-it!!!!BABY!!!!!!!~@#$%$#!)'(*@PO#JTKHEE.")

        # But CSS identifier rules are even stricter -- [^a-zA-Z0-9-]
        SAFE_FOR_ZOPE = "123456fck2_oh yeah, believe-itBABY~#$$#)(PO#JTKHEE."
        SAFE_FOR_CSS  = "fck2-oh-yeah--believe-itBABY-------PO-JTKHEE-"
        self.add(SAFE_FOR_ZOPE)
        self.assertEqual(hasattr(self.folder, SAFE_FOR_ZOPE), True)
        self.assertEqual(getattr(self.folder, SAFE_FOR_ZOPE).InstanceName
                        , SAFE_FOR_CSS )


class TestZopeFCKmanager(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        add = self.folder.manage_addProduct['FCKeditor'].manage_addFCKeditor
        add('fckmanager')
        self.fck = self.folder.fckmanager

    def testCanAddOtherObjectsProgrammatically(self):
        # afaict we in fact can't constrain programmatic addition of objects
        self.fck.manage_addProduct['OFSP'].manage_addFolder('foo')
        self.assertEqual(hasattr(self.fck, 'foo'), True)



##
# Assemble into a suite and run
##

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestZopeFCKeditor))
    suite.addTest(makeSuite(TestZopeFCKmanager))
    return suite

if __name__ == '__main__':
    framework()
