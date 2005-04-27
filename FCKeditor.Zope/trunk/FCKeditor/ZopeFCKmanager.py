# base classes
from OFS.SimpleItem import SimpleItem
from OFS.ObjectManager import ObjectManager
from OFS.PropertyManager import PropertyManager

# Zope
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products import meta_types

# us
#from Products.FCKeditor.FCKconnector import FCKconnector
from Products.FCKeditor.ZopeFCKeditor import ZopeFCKeditor


class ZopeFCKmanager(PropertyManager, SimpleItem):
    """provides API to support on-the-fly FCKeditor objects w/in Zope
    """

    security = ClassSecurityInfo()

    id = ''
    title = ''
    meta_type = 'FCKmanager'

    _properties=({'id':'title', 'type':'string', 'mode':'w'},)

    manage_options = PropertyManager.manage_options +\
                     SimpleItem.manage_options

    def __init__(self, id, title=''):
        self.id = id
        self.title = title

    security.declarePublic('spawn')
    def spawn(self, id):
        """given an id string, return an FCKeditor object
        """
        return ZopeFCKeditor(id)

#    security.declareProtected('Manage FCKmanager', 'setProperty')
#    def setProperty(self, key, val):
#        """support property assignment
#        """
#        setattr(self, key, val)

InitializeClass(ZopeFCKmanager)



##
# Product addition and registration
##

addForm = PageTemplateFile('www/addFCKmanager.pt', globals())

def manage_addFCKmanager(self, id, title='', REQUEST=None):
    """  """
    self._setObject(id, ZopeFCKmanager(id, title))
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

def initialize(context):
    context.registerClass(
        ZopeFCKmanager,
        permission='Add FCKmanager',
        constructors=(addForm, manage_addFCKmanager),
        icon='www/fckmanager.gif',
        )