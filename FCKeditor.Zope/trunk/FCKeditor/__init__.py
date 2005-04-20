from Products.CMFCore.DirectoryView import registerDirectory

FCKglobals = globals()

def initialize(context):
    registerDirectory('skins', FCKglobals)
