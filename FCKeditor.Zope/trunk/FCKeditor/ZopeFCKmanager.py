# base classes
from OFS.SimpleItem import SimpleItem
from OFS.ObjectManager import ObjectManager

# Zope
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile


class ZopeFCKmanager(SimpleItem, ObjectManager):
    """provides API for managing and supporting a set of FCKeditor objects from
    w/in Zope
    """

    security = ClassSecurityInfo()

    id = ''
    title = 'Manage a set of FCKeditors'
    meta_type = 'FCKmanager'

    manage_options = ({'label':'View', 'action':''},) +\
                     SimpleItem.manage_options

    def __init__(self, id, *arg, **kw):
        self.id = id

    security.declarePrivate('all_meta_types')
    def all_meta_types(self):
        """this overrides a method of ObjectManager that determines the kinds
        of objects that can be added here
        """
        return ['FCKeditor']


    ##
    # Management methods
    ##

    security.declarePublic('index_html')
    index_html = PageTemplateFile('www/manage_test.pt', globals())

InitializeClass(ZopeFCKmanager)



##
# Product addition and registration
##

manage_add = PageTemplateFile('www/manage_addFCKmanager.pt', globals())

def manage_addFCKmanager(self, id, REQUEST=None):
    """  """
    self._setObject(id, ZopeFCKeditor(id))
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

def initialize(context):
    context.registerClass(
        ZopeFCKmanager,
        permission='Add FCKmanager',
        constructors=(manage_add, manage_addFCKmanager),
        icon='www/fckmanager.gif',
        )