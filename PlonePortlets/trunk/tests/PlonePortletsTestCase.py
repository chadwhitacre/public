
from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

ZopeTestCase.installProduct('Archetypes')
ZopeTestCase.installProduct('PortalTransforms', quiet=1)
ZopeTestCase.installProduct('MimetypesRegistry', quiet=1)
ZopeTestCase.installProduct('PlonePortlets')

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager

from Acquisition import aq_base
import time

from Products.PlonePortlets import config
from Products.PlonePortlets.tests import utils

portal_owner = PloneTestCase.portal_owner
portal_name = PloneTestCase.portal_name


class PlonePortletsTestCase(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        utils.setupDummySession(self.app.REQUEST)
        self.portal.acl_users._doAddUser('PloneManager', '', ['Manager'], [])
 

def setupPlonePortlets(app, id=portal_name, quiet=0):
    portal = app[id]
    _start = time.time()
    if not quiet: ZopeTestCase._print('Adding PlonePortlets ... ')
    # Login as portal owner
    user = app.acl_users.getUserById(portal_owner).__of__(app.acl_users)
    newSecurityManager(None, user)
    # Add Archetypes
    if not hasattr(aq_base(portal), 'archetype_tool'):
        portal.portal_quickinstaller.installProduct('Archetypes')
    # Add PlonePortlets
    if not hasattr(aq_base(portal), 'portal_portlets'):
        portal.portal_quickinstaller.installProduct('PlonePortlets')
    # Log out
    noSecurityManager()
    get_transaction().commit()
    if not quiet: ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))


app = ZopeTestCase.app()
setupPlonePortlets(app)
ZopeTestCase.close(app)

