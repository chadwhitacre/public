from Products.CMFCore.DirectoryView import registerDirectory

# register tool
registerDirectory('root', globals())

def initialize(context):
    # Import lazily, and defer initialization to the module
    import BigCheeze
    BigCheeze.initialize(context)