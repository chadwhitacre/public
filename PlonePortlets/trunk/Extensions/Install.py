"""\
$id$

This file is an installation script for this skin.  
It is meant to be used as an External Method.  

To use, either use Plone 2.0+ quickinstaller to install, or add an external 
method to the root of the Plone Site that you want the skin registered 
in with the configuration:

 id: install_skin
 title: Install Skin *optional*
 module name: PlonePortlets.Instal
 function name: install

Then go to the management screen for the newly added external method
and click the 'Try it' tab.  
"""

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin

from Products.CMFCore.TypesTool import ContentFactoryMetadata
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.CMFCore.CMFCorePermissions import ManagePortal, SetOwnProperties, View

from cStringIO import StringIO
import string

from Products.PlonePortlets import PROJECTNAME, GLOBALS
from Products.PlonePortlets import PortletsTool
from Products.PlonePortlets import PlonePortlets_globals
from Products.PlonePortlets import portlets
from Products import PlonePortlets

from Products.PlonePortlets.Extensions.utils import registerPortlets, initializePortlet


skin_names = ('PlonePortlets','portlet_contents','PlonePortletPatches')

configlets = \
( { 'id'         : 'PlonePortlets'
  , 'name'       : 'Assign Portlets'
  , 'action'     : 'string:${portal_url}/prefs_portlets'
  , 'category'   : 'Products'
  , 'appId'      : 'PlonePortlets'
  , 'permission' : ManagePortal
  , 'imageUrl'  : 'skins_icon.gif'
  }
,
  { 'id'         : 'PlonePortletsAdd'
  , 'name'       : 'Add/Remove Portlets'
  , 'action'     : 'string:${portal_url}/portal_portlets'
  , 'category'   : 'Products'
  , 'appId'      : 'PlonePortlets'
  , 'permission' : ManagePortal
  , 'imageUrl'  : 'skins_icon.gif'
  }
,
  { 'id'         : 'PloneGroupPortlets'
  , 'name'       : 'Assign Portlets to groups'
  , 'action'     : 'string:${portal_url}/prefs_portlets_selectgroup'
  , 'category'   : 'Products'
  , 'appId'      : 'PlonePortlets'
  , 'permission' : ManagePortal
  , 'imageUrl'   : 'skins_icon.gif'
  }
,
    {'id':'MemberPortlets',
     'appId':'PlonePortlets',
     'name':'Personal Portlet Preferences',
     'action':'string:${portal_url}/personalize_portlets',
     'category':'Member',
     'permission': SetOwnProperties,
     'imageUrl':'skins_icon.gif'},
)


def setupSkin(self, out):
    skinsTool = getToolByName(self, 'portal_skins')
    
    # Add directory views
    try:  
        addDirectoryViews(skinsTool, 'skins', PlonePortlets_globals)
        out.write( "Added directory views to portal_skins.\n" )
    except:
        out.write( '*** Unable to add directory views to portal_skins.\n')

    # Go through the skin configurations and insert the skin
    skins = skinsTool.getSkinSelections()
    for skin in skins:
        path = skinsTool.getSkinPath(skin)
        path = map(string.strip, string.split(path,','))
        changed = 0
        for skin_name in skin_names:
            if skin_name not in path:
                try: 
                    path.insert(path.index('custom')+1, skin_name)
                    changed = 1
                except ValueError:
                    path.append(skin_name)
                    changed = 1

        if changed:        
            path = string.join(path, ', ')
            # addSkinSelection will replace existing skins as well.
            skinsTool.addSkinSelection(skin, path)
            out.write("Added %s to %s skin\n" % (', '.join(skin_names),skin))
        else:
            out.write("Skipping %s skin, %s already set up\n" % (skin, ', '.join(skin_names)))


def setupTool(self, out):
    # If there already is a portlets tool we leave it to avoid deleting existing portlet configurations
    if getToolByName(self, 'portal_portlets', None) is None:
        addTool = self.manage_addProduct['PlonePortlets'].manage_addTool
        addTool('PortletsTool')
        out.write('Adding Portlets Tool\n')

        catalog = getToolByName(self, 'portal_portlets')
        if getattr(catalog.Indexes, 'SearchableText', None) is not None:
            catalog.manage_delIndex(['SearchableText'])
        if getattr(catalog.Indexes, 'Subject', None) is not None:
            catalog.manage_delIndex(['Subject'])
        catalog.manage_addIndex('UID', 'FieldIndex')
        catalog.addColumn('UID')
        out.write('Fixing indexes in Portlets Tool\n')

    else:
        out.write('Portlets Tool already existed, skipping...\n')

    #def old_instll_types(self, out, types, package_name):        
    typesTool = getToolByName(self, 'portal_types')
    portal_type = 'PortletsTool'
##    try:
##        typesTool._delObject(type.portal_type)
##    except:
##        pass
    typeinfo_name = ""
    typesTool.manage_addTypeInformation('Factory-based Type Information',id='PortletsTool') 
    # Set the human readable title explicitly
    t = getattr(typesTool, 'PortletsTool', None)
    if t:
        t.title = 'PortletsTool'
        t.product = 'PlonePortlets'
        t.content_meta_type = 'PortletsTool'
        t.allowed_content_types = ('Portlet')
        t.content_icon = 'skins_icon.gif'

        t.addAction( 'View' , 'View' , 'string:${object_url}/folder_contents' , '' , (View,) , 'object' , visible=1 )

def addConfiglets(self, out):
    """ Adds the configlets to the Plone Control Panel """
    configTool = getToolByName(self, 'portal_controlpanel', None)
    if configTool:
        for conf in configlets:
            out.write('Adding configlet %s\n' % conf['id'])
            configTool.registerConfiglet(**conf)


def setupDefaultPortlets(self,out):
    """ instantiate and link the default portlets so that we see it working"""
    portletsTool = getToolByName(self, 'portal_portlets', None)
    initializePortlet(portletsTool,'StaticPortlet','confirmationportlet','column2',title='Success',body='PlonePortlets was sucessfully installed.')
    initializePortlet(portletsTool,'LoginPortlet','login','column1')
##def setupPortletCatalogLinks(self,classes):
##    ArchetypesTool = getToolByName(self, 'archetype_tool')
##    for klass in classes:
##        ArchetypesTool.setCatalogsByType(klass['meta_type'], ['portal_portlets','uid_catalog'])


def install(self):
    out = StringIO()
    setupSkin(self, out)
    setupTool(self, out)
    classes = listTypes(PROJECTNAME)
    installTypes(self, out,
                 classes,
                 PROJECTNAME)
    #setupPortletCatalogLinks(self,classes)
    registerPortlets(self,classes)
    addConfiglets(self, out)
    setupDefaultPortlets(self,out)
    out.write('Installation completed.\n')
    return out.getvalue()


#
# Uninstall methods
#

def removeConfiglets(self, out):
    configTool = getToolByName(self, 'portal_controlpanel', None)
    if configTool:
        for conf in configlets:
            out.write('Removing configlet %s\n' % conf['id'])
            configTool.unregisterConfiglet(conf['id'])


def uninstall(self):
    out = StringIO()
    removeConfiglets(self, out)
    out.write('manual uninstall completed.\n')
    return out.getvalue()

