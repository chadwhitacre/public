"""
NavTreePortlet
"""
from Products.CMFCore.utils import getToolByName, ContentInit
from Products.CMFCore.DirectoryView import registerDirectory
from Products.Archetypes.public import *
from Products.Archetypes import listTypes
from Products.NavTreePortlet.config import SKINS_DIR, GLOBALS, PROJECTNAME, ADD_CONTENT_PERMISSION

from Products.NavTreePortlet.NavTreePortlet import NavTreePortlet


def initialize(context):
    # register directory views
    registerDirectory('skins', GLOBALS)

    # content initialization
    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME), PROJECTNAME,
        )

    ContentInit(
        '%s Content' % PROJECTNAME,
        content_types = content_types,
        permission = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti = ftis,
        ).initialize(context)