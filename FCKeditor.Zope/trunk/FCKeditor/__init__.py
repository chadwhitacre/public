# Imports
# =======

from AccessControl import allow_class
from FCKexception import FCKexception  # the next import imports this from here
from FCKeditor import FCKeditor as ZopeFCKeditor # so import order is important



# Conditional Imports
# ===================

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
    from Products.FCKeditor.PloneFCKeditor import PloneFCKeditor
    from Products.FCKeditor import PloneFCKconnector
except ImportError:
    Plone = False



# Expose PloneFCKeditor to restricted Python.
# ===========================================

if Plone:
    allow_class(PloneFCKeditor)



# Initialize the Product.
# =======================

FCKglobals = globals()
def initialize(registrar):

    if CMFCore:
        registerDirectory('skins', FCKglobals)

    if Plone:
        PloneFCKconnector.initialize(registrar)
