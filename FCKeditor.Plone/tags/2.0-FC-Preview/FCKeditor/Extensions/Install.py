###
# FCKEditor2-Installer-Script for CMF
# Taken and adapted from CMFVisualEditor and Epoz
###

from Products.FCKeditor import fckeditor_globals
from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.DirectoryView import addDirectoryViews

SKIN_NAME = "editor_fck"
_globals = globals()

def install_plone(self, out):
    """ add FCK Editor to 'my preferences' """
    portal_props=getToolByName(self,'portal_properties')
    site_props=getattr(portal_props,'site_properties', None)
    attrname='available_editors'
    if site_props is not None:
        editors=list(site_props.getProperty(attrname)) 
        if 'FCK Editor' not in editors:
           editors.append('FCK Editor')
        site_props._updateProperty(attrname, editors)        
        print >>out, "Added FCKeditor 2.0 Final Candidate (Preview) to available editors in Plone."

def install_subskin(self, out, skin_name=SKIN_NAME, globals=fckeditor_globals):
    skinstool=getToolByName(self, 'portal_skins')
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
    print >>out, "Installing FCKeditor 2.0 Final Candidate (Preview)"
    
    install_subskin(self, out)
    install_plone(self, out)

    print >>out, "Done."
    
    return out.getvalue()
