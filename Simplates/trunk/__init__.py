import FSSimplate # this is just so we can auto-refresh it

from Products.CMFCore.DirectoryView import registerDirectory
registerDirectory('skins', globals())


# Placeholder for Zope Product data
#misc_ = {}

def initialize(context):
    # Import lazily, and defer initialization to the module
    import ZopeSimplate
    ZopeSimplate.initialize(context)