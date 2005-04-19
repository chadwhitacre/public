from Products.CMFCore.DirectoryView import registerDirectory

def initialize(context):
    registerDirectory('skins', globals())
