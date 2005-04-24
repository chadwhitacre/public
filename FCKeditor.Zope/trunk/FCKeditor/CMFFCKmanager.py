# base classes
from Products.FCKeditor.ZopeFCKmanager import ZopeFCKmanager
from Products.CMFCore.utils import UniqueObject

# Zope
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile


class CMFFCKmanager(ZopeFCKmanager, UniqueObject):
    """a CMF tool to support a set of FCKeditor objects
    """

    security = ClassSecurityInfo()

    id = 'portal_fckmanager'
    title = 'Manage a set of FCKeditors'
    meta_type = 'CMFFCKmanager'

    def __init__(self, *arg, **kw):
        pass




    ##
    # Management methods
    ##

    security.declarePublic('index_html')
    index_html = PageTemplateFile('www/manage_test.pt', globals())

InitializeClass(CMFFCKmanager)



##
# Product addition and registration
##

manage_add = PageTemplateFile('www/manage_addCMFFCKmanager.pt', globals())

def manage_addFCKmanager(self, id, REQUEST=None):
    """  """
    self._setObject(id, ZopeFCKeditor(id))
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

def initialize(context):
    context.registerClass(
        ZopeFCKeditor,
        permission='Add FCKmanager',
        constructors=(manage_add, manage_addFCKeditor),
        icon='www/fckmanager.gif',
        )