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
    from Products.FCKeditor import PloneFCKconnector
except ImportError:
    Plone = False



# Prepare FCKeditor for Zope
# ==========================
# Not sure if this is goofy or cool, but we are wrapping the FCKeditor class
# for Zope in here rather than in a full-blown class. Given the usage pattern
# for FCKeditor (on the fly from Scripts (Python)) I think this is fine. In
# other words, ZopeFCKeditors aren't intended to be stored.

# can't mess with non-method attrs directly, so set up some setters
def SetConfig(self, key, val):
    self.Config[key] = val
setattr(ZopeFCKeditor, 'SetConfig', SetConfig)

def SetProperty(self, key, val):
    self.__dict__[key] = val
setattr(ZopeFCKeditor, 'SetProperty', SetProperty)

# and let us use the whole class unfettered from Scripts (Python), etc.
# usage: from Products.FCKeditor import ZopeFCKeditor
allow_class(ZopeFCKeditor)



# Product Initialization
# ======================

FCKglobals = globals()
def initialize(registrar):

    if CMFCore:
        registerDirectory('skins', FCKglobals)

    if Plone:
        PloneFCKconnector.initialize(registrar)
