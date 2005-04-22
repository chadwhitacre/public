try:
    from Products.CMFCore.DirectoryView import registerDirectory
    CMF = True
except ImportError:
    CMF = False

FCKglobals = globals()

def initialize(context):
    if CMF: registerDirectory('skins', FCKglobals)

    import ZopeFCKeditor
    ZopeFCKeditor.initialize(context)
