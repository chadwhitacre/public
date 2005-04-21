# Zope
from Acquisition import Implicit
from Persistence import Persistent
from AccessControl.Role import RoleManager
from OFS.SimpleItem import Item

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile


# us
from FCKeditor import FCKeditor

class ZopeFCKeditor(FCKeditor, Implicit, Persistent, RoleManager, Item):
    """A Zope wrapper around FCKeditor
    """

    security = ClassSecurityInfo()

    id = ''
    title = ''
    meta_type = 'FCKeditor'

    def __init__(self, id, *arg, **kw):

        self.id = id

        FCKeditor.__init__(self, *arg, **kw)

    def Compatible(self):
        """only actually meaningful in Zope-space
        """
        return True


InitializeClass(ZopeFCKeditor)



##
# Product addition and registration
##

manage_add = PageTemplateFile('www/manage_add.pt', globals())

def manage_addFCKeditor(self, id, REQUEST=None):
    """  """
    self._setObject(id, ZopeFCKeditor(id))
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

def initialize(context):
    context.registerClass(
        ZopeFCKeditor,
        permission='Add FCKeditor',
        constructors=(manage_add, manage_addFCKeditor),
        icon='www/icon.gif',
        )