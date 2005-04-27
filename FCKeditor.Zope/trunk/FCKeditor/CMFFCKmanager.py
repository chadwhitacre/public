# base classes
from Products.FCKeditor.ZopeFCKmanager import ZopeFCKmanager
from Products.CMFCore.utils import UniqueObject

# Zope
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

ID = 'portal_fckmanager'

class CMFFCKmanager(ZopeFCKmanager, UniqueObject):
    """a CMF tool to support on-the-fly FCKeditor objects
    """

    id = ID
    title = 'Manage a set of FCKeditors'
    meta_type = 'FCKmanager for CMF'


InitializeClass(CMFFCKmanager)



##
# Product addition and registration
##

def manage_addCMFFCKmanager(self, REQUEST=None):
    """  """
    self._setObject(ID, CMFFCKmanager(ID))
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

def initialize(context):
    context.registerClass(
        CMFFCKmanager,
        permission='Add FCKmanager for CMF',
        constructors=(manage_addCMFFCKmanager,),
        icon='www/fckmanager.gif',
        )