from Products.CMFCore.DirectoryView import registerDirectory

# register tool
registerDirectory('root', globals())

def initialize(context):
    # Import lazily, and defer initialization to the module
    import Cheese
    Cheese.initialize(context)