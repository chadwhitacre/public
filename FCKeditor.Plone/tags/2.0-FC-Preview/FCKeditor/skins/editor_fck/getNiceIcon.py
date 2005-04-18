## Script (Python) "fck_browseFiles"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj
##title=
##
try:
 from Products.CMFCore.utils import getToolByName
 registry = getToolByName(context, 'mimetypes_registry')

 if obj.portal_type in ('File', 'Image', 'Photo', 'ZPhoto') :
  try:
    ct=obj.content_type
    mt=registry.lookup(ct)[0]
    return mt.icon_path
  except:
    return obj.getIcon(1)

 return obj.getIcon(1)

except:
 return obj.getIcon(1)