## Script (Python) "additional_style_props"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
base_props = context.base_properties_dict()
portal = context.portal_url.getPortalObject()
logo = context.restrictedTraverse(base_props['logoName'])

return {
    'portal_url' : portal.absolute_url(),
    'logoWidth'  : logo.width,
    'logoHeight' : logo.height,
    }
