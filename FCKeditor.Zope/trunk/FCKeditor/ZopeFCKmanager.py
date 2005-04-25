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
from Products.FCKeditor.FCKconnector import FCKconnector


# base class order is important
class ZopeFCKmanager(ObjectManager, PropertyManager, SimpleItem):
    """provides API for managing and supporting a set of FCKeditor objects from
    w/in Zope
    """

    security = ClassSecurityInfo()

    id = ''
    title = ''
    meta_type = 'FCKmanager'

    _properties=({'id':'title', 'type':'string', 'mode':'w'},)

    manage_options = ObjectManager.manage_options +\
                     PropertyManager.manage_options +\
                     SimpleItem.manage_options

    def __init__(self, id, title=''):
        self.id = id
        if title: self.title = title

    security.declarePrivate('all_meta_types')
    def all_meta_types(self):
        """this overrides a method of ObjectManager that determines the kinds
        of objects that are displayed as addable on manage_main; I don't see a
        way to constrain programmatic object addition
        """
        meta_types = ObjectManager.all_meta_types(self)
        return [m for m in meta_types if m['name'] == 'FCKeditor']

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