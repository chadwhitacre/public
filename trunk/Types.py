from Products.CMFCore.utils import getToolByName


##
# portal_types
##

def uninstallTypes(portal, types_to_remove):
    typesTool = getToolByName(portal, 'portal_types')
    for t in types_to_remove:
        typesTool._delObject(t)
