#BOILERPLATE###################################################################
#                                                                             #
#  This package wraps FCKeditor for use in the Zope web application server.   #
#  Copyright (C) 2005 Chad Whitacre <http://www.zetadev.com/>                 #
#                                                                             #
#  This library is free software; you can redistribute it and/or modify it    #
#  under the terms of the GNU Lesser General Public License as published by   #
#  the Free Software Foundation; either version 2.1 of the License, or (at    #
#  your option) any later version.                                            #
#                                                                             #
#  This library is distributed in the hope that it will be useful, but        #
#  WITHOUT ANY WARRANTY; without even the implied warranty of                 #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser    #
#  General Public License for more details.                                   #
#                                                                             #
#  You should have received a copy of the GNU Lesser General Public License   #
#  along with this library; if not, write to the Free Software Foundation,    #
#  Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA                #
#                                                                             #
###################################################################BOILERPLATE#
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

    if 'FCKcache' not in self.objectIds():
        self._setObject('FCKcache', AcceleratedHTTPCacheManager('FCKcache'))
        cache_settings = { 'anonymous_only' : 0
                         , 'notify_urls'    : ()
                         , 'interval'       : 36000
                          }
        self.FCKcache.manage_editProps( 'HTTPCache for FCKeditor'
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
        if 'FCKeditor' not in editors:
           editors.append('FCKeditor')
        site_props._updateProperty(attrname, editors)

        print >> out, "Added FCKeditor to available editors in Plone."

    # add a PloneFCKconnector
    self.manage_addProduct['FCKeditor'].manage_addPloneFCKconnector()


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
    def fail():
        raise "It looks like you haven't yet run utils/base2zope.py"
    fckeditor_base = os.path.join('..', 'skins', 'fckeditor_base', 'FCKeditor')
    if not os.path.isdir(fckeditor_base): fail()
    if len(os.listdir(fckeditor_base)) <= 1: fail() # account for .svn

    # do the installation
    install_cache(self, out)
    install_plone(self, out)
    install_subskin(self, out, 'fckeditor_plone')
    install_subskin(self, out, 'fckeditor_base')

    print >> out, "FCKeditor installation done."

    return out.getvalue()
