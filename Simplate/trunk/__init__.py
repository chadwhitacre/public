from Products.CMFCore.DirectoryView import registerDirectory
import ZopeSimplate

registerDirectory('skins', globals())

def initialize(context):
    # Import lazily, and defer initialization to the module
    import ZopeSimplate
    ZopeSimplate.initialize(context)