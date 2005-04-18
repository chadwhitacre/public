
global fckeditor_globals
fckeditor_globals=globals()

from Products.CMFCore.DirectoryView import registerDirectory

def initialize(context):
    registerDirectory('skins', fckeditor_globals)
