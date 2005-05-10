# Do we have CMFCore?
try:
    from Products.CMFCore.DirectoryView import registerDirectory
    CMFCore = True
except ImportError:
    CMFCore = False

# Do we have CMFPlone?
try:
    from Products import CMFPlone
    Plone = True
except:
    Plone = False


FCKglobals = globals()

def initialize(context):

    if CMFCore:
        registerDirectory('skins', FCKglobals)

    import ZopeFCKeditor
    ZopeFCKeditor.initialize(context)

    if Plone:
        import PloneFCKmanager
        PloneFCKmanager.initialize(context)


class FCKexception(Exception):
    """Error within the FCK connector application"""
