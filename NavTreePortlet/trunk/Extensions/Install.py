"""\
Install script for NavTreePortlet
"""

from Products.CMFCore.TypesTool import ContentFactoryMetadata
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin

from Products.NavTreePortlet.config import PROJECTNAME, GLOBALS
from Products.NavTreePortlet.NavTreePortlet import NavTreePortlet

from cStringIO import StringIO
import string


from Products.PlonePortlets.Extensions.utils import registerPortlets, initializePortlet

def installExtendedPathIndex(self, out):
    ct = getToolByName(self, 'portal_catalog')
    ct.delIndex('path')
    ct.addIndex('path', 'ExtendedPathIndex')
    ct.refreshCatalog(clear=1)

    
def installPortlet(self, out):
    types = listTypes(PROJECTNAME)
    registerPortlets(self, types)
    #id = 'sitemap'
    #sitemap = NavTreePortlet(id)
    #self._setObject(id, sitemap)
    #sitemap = getattr(self, id)
    #sitemap.initializeArchetype(title='Sitemap')
    #pt = getToolByName(self, 'portal_portlets')
    #pt.addPortletToSection(self, sitemap.UID(), 'column1')
    initializePortlet(self,'NavTreePortlet','navtree','column1',title="Navigation")

def install(self):
    out=StringIO()

    if not hasattr(self, "_isPortalRoot"):
        print >> out, "Must be installed in a CMF Site (read Plone)"
        return
    
    print >> out, "Installing %s" % listTypes(PROJECTNAME)
    
    qi = getToolByName(self, 'portal_quickinstaller', None)
    qi.installProduct('PlonePortlets',)

    installTypes(self, out, listTypes(PROJECTNAME), PROJECTNAME)

    installExtendedPathIndex(self, out)

    installPortlet(self, out)

    install_subskin(self, out, GLOBALS)

    print >> out, 'Successfully installed types.'

    return out.getvalue()

def uninstall(self):
    out=StringIO()
    out.write('manual uninstall completed.\n')
    return out.getvalue()

