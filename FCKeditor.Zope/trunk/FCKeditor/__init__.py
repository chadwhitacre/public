import sys

try:
    from Products.CMFCore.DirectoryView import registerDirectory
    CMFCore = True
except ImportError:
    CMFCore = False

try:
    from Products import CMFPlone
    Plone = True
except:
    Plone = False


FCKglobals = globals()

def initialize(context):

    if CMFCore:
        registerDirectory('skins', FCKglobals)

    import ZopeFCKeditor, ZopeFCKmanager

    ZopeFCKeditor.initialize(context)
    ZopeFCKmanager.initialize(context)

    if Plone:
        import PloneFCKmanager
        PloneFCKmanager.initialize(context)
