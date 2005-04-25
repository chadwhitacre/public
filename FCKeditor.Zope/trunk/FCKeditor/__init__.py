try:
    from Products.CMFCore.DirectoryView import registerDirectory
    CMFCore = True
except ImportError:
    CMFCore = False

FCKglobals = globals()

def initialize(context):

    if CMFCore: registerDirectory('skins', FCKglobals)

    import ZopeFCKeditor, ZopeFCKmanager, CMFFCKmanager
    ZopeFCKeditor.initialize(context)
    ZopeFCKmanager.initialize(context)
    CMFFCKmanager.initialize(context)
