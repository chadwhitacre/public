import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.PlonePortlets.tests import PlonePortletsTestCase

from Products.PlonePortlets.tests import utils
from Products.PlonePortlets.Extensions import utils as installutils

from Products.CMFCore.utils import getToolByName
from Acquisition import aq_base, aq_chain, aq_parent
from AccessControl import getSecurityManager


class TestPlonePortlets(PlonePortletsTestCase.PlonePortletsTestCase):
    """ Testing Plone Portlets"""

    def afterSetUp(self):
        PlonePortletsTestCase.PlonePortletsTestCase.afterSetUp(self)
        self.pp = self.portal.portal_portlets
        self.loginPortalOwner()

    def testToolExists(self):
        self.failUnless(hasattr(aq_base(self.portal), 'portal_portlets'))

    def testAddPortlet(self):
        utils.makePortlet(self.pp)
        self.failUnless('portlet' in self.pp.objectIds())

    def testCatalogingPortlet(self):
        utils.makePortlet(self.pp)
        self.failUnless(self.pp.searchResults())
        self.failUnless(self.pp.searchResults()[0].UID)
        self.failUnless(self.portal.uid_catalog.searchResults())

    def testPortletNotIndexedInPortalCatalog(self):
        utils.makePortlet(self.pp)
        self.failIf(self.portal.portal_catalog.searchResults(meta_type='Portlet'))

    def testContextWrapping(self):
        p = utils.makePortlet(self.pp)
        p = self.pp._rewrapPortlet(p, self.portal)
        self.failUnless(aq_parent(p) == self.portal)
        folder = utils.makeContent(self.portal, 'Folder', id='folder')
        p = self.pp._rewrapPortlet(p, folder)
        self.failUnless(aq_parent(p) == folder)

    # filtering out is currently broken. We can enable this test again when it is fixed. 
    def testFilteringOut(self):
        p = utils.makePortlet(self.pp)
        folder = utils.makeContent(self.portal, 'Folder', id='folder')
        portletuid = p.UID()
        self.pp.addPortletToSection(self.portal,portletuid,'col1')
        folder.portletsdata={'filterOut':[portletuid]}
        self.failIf(self.pp.getPortletsSection(folder,'col1'))

    def testRenderingPortletGroup(self):
        p = utils.makePortlet(self.pp,body='test')
        portletuid = p.UID()
        self.pp.addPortletToSection(self.portal,portletuid,'col1')
        self.failUnless(self.pp.renderPortletsSection(self.portal,'col1'))

    def testRenderingEmptyPortletGroup(self):
        p = utils.makePortlet(self.pp)
        p.setCondition('nothing')
        portletuid = p.UID()
        self.pp.addPortletToSection(self.portal,portletuid,'col1')
        self.failIf(self.pp.renderPortletsSection(self.portal,'col1'))

    def testRenderingPortletGroupWithWrongGroupDefined(self):
        p = utils.makePortlet(self.pp)
        portletuid = p.UID()
        self.pp.addPortletToSection(self.portal,portletuid,'col2')
        self.failIf(self.pp.renderPortletsSection(self.portal,'col1'))

    def testAddPortletToSection(self):
        p = utils.makePortlet(self.pp,body="test")
        portletuid = p.UID()
        self.pp.addPortletToSection(self.portal,portletuid,'col1')
        self.failUnless(len(self.pp.getPortletsSection(self.portal,'col1'))==1)
        self.failUnless(self.pp.renderPortletsSection(self.portal,'col1'))

    def testAddPortletToTwoGroups(self):
        p = utils.makePortlet(self.pp)
        portletuid = p.UID()
        self.pp.addPortletToSection(self.portal,portletuid,'col2')
        self.pp.addPortletToSection(self.portal,portletuid,'col1')
        self.failUnless(self.pp.getPortletsSection(self.portal,'col1'))
        self.failUnless(self.pp.getPortletsSection(self.portal,'col2')[0].UID == portletuid)

    def testRemovingPortletFromGroup(self):
        p = utils.makePortlet(self.pp)
        portletuid = p.UID()
        self.pp.addPortletToSection(self.portal,portletuid,'col1')
        self.pp.removePortletFromSection(self.portal,portletuid,'col1')
        self.failUnless(hasattr(self.portal,'portletsdata'))
        self.failIf(self.portal.portletsdata['col1'])
##
##    def testPortletsAvailabilityWithPermissions(self):
##        p = utils.makePortlet(self.pp)
##        self.portal.acl_users._doAddUser('user1', 'secret', ['Member'], [])
##        self.login('user1')
##        self.failIf(len(self.pp.getAvailablePortlets())>0)
        
    def testRenamePortlet(self):
        p = utils.makePortlet(self.pp)
        get_transaction().commit(1)
        self.pp.manage_renameObject(p.getId(), 'newportletname')
        self.failUnless('newportletname' in self.pp.objectIds())

    def testUserGroups(self):
        self.login('PloneManager')
        groupstool = self.portal.portal_groups
        groupstool.groupWorkspacesCreationFlag = 0
        groupstool.addGroup('foo', '', [], [])
        g = groupstool.getGroupById('foo')
        g.addMember('PloneManager')
        self.assertEqual(g.getGroupMembers()[0].getId(), 'PloneManager')
        # we now know we are actually a member of group foo

    def testUserGroupPortlets(self):
        self.login('PloneManager')
        groupstool = self.portal.portal_groups
        groupstool.groupWorkspacesCreationFlag = 0
        groupstool.addGroup('foo', '', [], [])
        g = groupstool.getGroupById('foo')
        g.addMember('PloneManager')

        p = utils.makePortlet(self.pp)
        self.pp.setPortletsSection( [p.UID], 'column1', context=None, usergroup='foo')
        username = getSecurityManager().getUser().getUserName()
        self.failUnless(len(self.pp.getMyGroupPortlets()) > 0 )

    def testPortletVisibilityInContext(self):
        self.login('PloneManager')
        p = utils.makePortlet(self.pp, body='test')
        self.failUnless(p.portletVisibilityInContext(self.portal))
        p.setCondition('python:0')
        self.failIf(p.portletVisibilityInContext(self.portal))
        p.setCondition('python:1')
        self.failUnless(p.portletVisibilityInContext(self.portal))

    def testNewPortletToSection(self):
        p = utils.makePortlet(self.pp)
        portletuid = p.UID()
        self.pp.setPortletsSection([portletuid], 'col1')
        #raise (str(getattr(self.pp.aq_base,'meta_type')))
        
        self.failUnless( self.pp.findPortletsForContext(self.pp) )
        self.failUnless( self.pp.getPortletsSection(self.pp,'col1') )
        self.failUnless( self.pp.getPortletsSectionExplicit(self.pp,'col1') )
        

    def testInstallUtils(self):
        installutils.instantiatePortlet(self.pp,'Portlet','portlet',condition='A')
        self.failUnless('portlet' in self.pp.objectIds())
        self.failUnless(self.pp.portlet.getCondition()=='A')

    def testInstallUtils2(self):
        installutils.initializePortlet(self.pp,'Portlet','portlet','col1',condition='A')
        self.failUnless('portlet' in self.pp.objectIds())
        self.failUnless(self.pp.portlet.getCondition()=='A')
        self.failUnless(len(self.pp.getPortletsSection(self.portal,'col1'))==1)

    #def testPortletCss(self):
    #    installutils.initializePortlet(self.pp,'Portlet','portlet','col1',condition='A')
    #    self.failUnless(self.pp.getHelperCSS(self.portal))
	
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPlonePortlets))
    return suite

if __name__ == '__main__':
    framework()
