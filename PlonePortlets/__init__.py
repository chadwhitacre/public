"""
$Id: __init__.py,v 1.1 2004/01/27 10:48:48 elvix Exp $
"""

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore import utils
from config import SKINS_DIR, GLOBALS, PROJECTNAME

from Products.PlonePortlets.portletClasses import *
from Products.Archetypes.public import *

from config import ADD_CONTENT_PERMISSION

import BasePortlet
import PortletsTool

PlonePortlets_globals=globals()

# Make the skins available as DirectoryViews.
registerDirectory('skins', PlonePortlets_globals)


def initialize(context):
    
   # process our custom types

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    utils.ContentInit(
        PROJECTNAME + ' Content',
        content_types = content_types,
        permission = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti = ftis,
        ).initialize(context)

    utils.ToolInit('Portlets Tool', 
            tools=(PortletsTool.PortletsTool, ), 
            product_name='PlonePortlets',
            icon='tool.gif'
            ).initialize(context)
    
