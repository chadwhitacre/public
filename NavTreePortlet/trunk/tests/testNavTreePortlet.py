import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.NavTreePortlet.tests import NavTreePortletTestCase
from Products.NavTreePortlet.tests import utils
from Products.NavTreePortlet.config import PROJECTNAME

from Products.CMFCore.utils import getToolByName
from Acquisition import aq_base, aq_chain, aq_parent
from AccessControl import getSecurityManager


class TestNavTreePortlet(NavTreePortletTestCase.NavTreePortletTestCase):
    """ Testing """

    def testProductInstall(self):
        qi = self.portal.portal_quickinstaller
        self.failUnless(qi.isProductInstalled(PROJECTNAME))

    def testSitemapInstall(self):
        self.failUnless('navtree' in self.portal.portal_portlets.objectIds())
        
    def testTreeBuilder(self):
        self.loginPortalOwner()
        self.portal.invokeFactory('Document','doc1')
        self.portal.invokeFactory('Document','doc2')
        self.portal.invokeFactory('Document','doc3')
        self.portal.invokeFactory('Folder','folder1')
        folder1 = getattr(self.portal, 'folder1')
        folder1.invokeFactory('Document','doc11')
        folder1.invokeFactory('Document','doc12')
        folder1.invokeFactory('Document','doc13')
        self.portal.invokeFactory('Folder','folder2')
        folder2 = getattr(self.portal, 'folder2')
        folder2.invokeFactory('Document','doc21')
        folder2.invokeFactory('Document','doc22')
        folder2.invokeFactory('Document','doc23')
        raw_portlet = self.portal.portal_portlets.navtree
        portlettool = self.portal.portal_portlets

        portlet = portlettool._rewrapPortlet(raw_portlet, self.portal.folder1)
        res = portlet._fetchPortletData()

        portlet = portlettool._rewrapPortlet(raw_portlet, self.portal.folder2)
        res2 = portlet._fetchPortletData()

        self.logout()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestNavTreePortlet))
    return suite

if __name__ == '__main__':
    framework()
