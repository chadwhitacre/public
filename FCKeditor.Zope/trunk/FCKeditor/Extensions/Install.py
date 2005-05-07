# Python
import os
from StringIO import StringIO

# Zope
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.StandardCacheManagers.AcceleratedHTTPCacheManager \
                             import AcceleratedHTTPCacheManager

# us
from Products.FCKeditor import FCKglobals



def install_cache(self, out):
    """ Add an HTTPCache specifically for FCKeditor.

    Apparently this is for better compatibility with non-Plone CMF apps.

    """

    if 'FCKCache' not in self.objectIds():
        self._setObject('FCKCache', AcceleratedHTTPCacheManager('FCKCache'))
        cache_settings = { 'anonymous_only' : 0
                         , 'notify_urls'    : ()
                         , 'interval'       : 36000
                          }
        self.FCKCache.manage_editProps( 'HTTPCache for FCKeditor'
                                      , settings = cache_settings
                                      )
        print >> out, "Added FCKeditor HTTPCache"



def install_plone(self, out):
    """Add FCKeditor to 'My Preferences'.
    """
    portal_props = getToolByName(self, 'portal_properties')
    site_props = getattr(portal_props, 'site_properties', None)
    attrname='available_editors'

    if site_props is not None:

        editors = list(site_props.getProperty(attrname))
        if 'FCK Editor' not in editors:
           editors.append('FCK Editor')
        site_props._updateProperty(attrname, editors)

        print >> out, "Added FCKeditor 2.0 Final Candidate (Preview) to " +\
                      "available editors in Plone."

    # add a CMFFCKmanager and tweak the FolderTypes
    self.manage_addProduct['FCKeditor'].manage_addCMFFCKmanager()
    self.portal_fckmanager.FolderTypes = ('Plone Folder',)


def install_subskin(self, out, skin_name, globals=FCKglobals):
    """Add a skin to portal_skins.
    """
    skinstool = getToolByName(self, 'portal_skins')
    if skin_name not in skinstool.objectIds():
        addDirectoryViews(skinstool, 'skins', globals)

    for skinName in skinstool.getSkinSelections():
        path = skinstool.getSkinPath(skinName)
        path = [i.strip() for i in  path.split(',')]
        try:
            if skin_name not in path:
                path.insert(path.index('custom') +1, skin_name)
        except ValueError:
            if skin_name not in path:
                path.append(skin_name)

        path = ','.join(path)
        skinstool.addSkinSelection( skinName, path)



def install(self):
    out = StringIO()

    print >> out, "Installing FCKeditor.Zope 0.1"

    # check to see if base2zope has been run
    #def fail():
    #    raise "It looks like you haven't yet run utils/base2zope.py"
    #fckeditor_base = os.path.join('..', 'skins', 'fckeditor_base', 'FCKeditor')
    #if not os.path.isdir(fckeditor_base): fail()
    #if len(os.listdir(fckeditor_base)) <= 1: fail() # account for .svn

    # do the installation
    install_cache(self, out)
    install_plone(self, out)
    install_subskin(self, out, 'fckeditor_plone')
    install_subskin(self, out, 'fckeditor_base')

    print >> out, "FCKeditor installation done."

    return out.getvalue()
