
from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

ZopeTestCase.installProduct('Archetypes')
ZopeTestCase.installProduct('PortalTransforms', quiet=1)
ZopeTestCase.installProduct('MimetypesRegistry', quiet=1)
ZopeTestCase.installProduct('PlonePortlets')
ZopeTestCase.installProduct('ExtendedPathIndex')
ZopeTestCase.installProduct('NavTreePortlet')

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager

from Acquisition import aq_base
import time

from Products.NavTreePortlet import config
from Products.NavTreePortlet.tests import utils

portal_owner = PloneTestCase.portal_owner
portal_name = PloneTestCase.portal_name


class NavTreePortletTestCase(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        utils.setupDummySession(self.app.REQUEST)
        self.portal.acl_users._doAddUser('PloneManager', '', ['Manager'], [])
 

def setupNavTreePortlet(app, id=portal_name, quiet=0):
    portal = app[id]
    _start = time.time()
    if not quiet: ZopeTestCase._print('Adding NavTreePortlet ... ')
    # Login as portal owner
    user = app.acl_users.getUserById(portal_owner).__of__(app.acl_users)
    newSecurityManager(None, user)
    # Add Archetypes
    if not hasattr(aq_base(portal), 'archetype_tool'):
        portal.portal_quickinstaller.installProduct('Archetypes')
    # Add PlonePortlets
    if not hasattr(aq_base(portal), 'portal_portlets'):
        portal.portal_quickinstaller.installProduct('PlonePortlets')
    # Add NavTreePortlet
    if not hasattr(aq_base(portal), 'sitemap'):
        portal.portal_quickinstaller.installProduct('NavTreePortlet')
    # Log out
    noSecurityManager()
    get_transaction().commit()
    if not quiet: ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))


app = ZopeTestCase.app()
setupNavTreePortlet(app)
ZopeTestCase.close(app)

