#
# Skeleton ExtendedPathIndexTestCase
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

from Products.ExtendedPathIndex.tests import ExtendedPathIndexTestCase
from Products.ExtendedPathIndex.tests import dummy
from Products.ExtendedPathIndex.tests import utils


class TestSomeProduct(ExtendedPathIndexTestCase.ExtendedPathIndexTestCase):

    def afterSetUp(self):
        pass

    def testSomething(self):
        # Test something
        self.failUnless(1==1)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSomeProduct))
    return suite

if __name__ == '__main__':
    framework()
