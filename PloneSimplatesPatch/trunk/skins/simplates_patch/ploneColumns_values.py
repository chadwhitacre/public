## Script (Python) "ploneColumns_values"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
base_props = context.base_properties_dict()

# we have this script in here so that replicate the default settings in stock 
# ploneColumns.css 


defaults = {
    'portalMinWidth':'70em',
    'columnTwoWidth':'16em',
    'columnOneWidth':'16em',
    }

for key in defaults.keys():
    if base_props[key] == '':
        base_props[key] = defaults[key]

return base_props
