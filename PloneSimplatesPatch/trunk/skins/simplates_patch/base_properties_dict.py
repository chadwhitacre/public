## Script (Python) "base_properties_dict"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
old_base = context.base_properties
new_base = {}
for key, value in old_base.propertyItems():
    new_base[key]=value

return new_base
