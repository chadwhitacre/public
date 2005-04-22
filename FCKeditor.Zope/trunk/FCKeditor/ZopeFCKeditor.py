# Python
import types

# Zope
from Acquisition import Implicit
from Persistence import Persistent
from AccessControl.Role import RoleManager
from OFS.SimpleItem import Item
from OFS.PropertyManager import PropertyManager

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import ExtensionClass

# us
from FCKeditor import FCKeditor

class ZopeFCKeditor(FCKeditor, Implicit, Persistent, PropertyManager, \
                    RoleManager, Item):
    """A Zope wrapper around FCKeditor
    """

    security = ClassSecurityInfo()
    security.declarePublic('Create')
    security.declarePrivate('Compatible')
    security.declarePublic('GetConfigQuerystring')
    security.declarePublic('SetConfig')

    id = ''
    title = ''
    meta_type = 'FCKeditor'

    _properties = ( {'id':'InstanceName',   'type':'string', 'mode':'w'}
                  , {'id':'Width',          'type':'string', 'mode':'w'}
                  , {'id':'Height',         'type':'string', 'mode':'w'}
                  , {'id':'ToolbarSet',     'type':'string', 'mode':'w'}
                  , {'id':'Value',          'type':'string', 'mode':'w'}
                  , {'id':'BasePath',       'type':'string', 'mode':'w'}
                   )

    manage_options = PropertyManager.manage_options +\
                     ({'label':'View', 'action':''},) +\
                     RoleManager.manage_options +\
                     Item.manage_options

    def __init__(self, id, *arg, **kw):
        self.id = id
        FCKeditor.__init__(self, *arg, **kw)
        self._propertize_attrs()

    security.declarePrivate('_propertize_attrs')
    def _propertize_attrs(self):
        """In our base class we want to use instance attrs so that we can use
        self.__dict__. However, self.__dict__ doesn't contain class attrs, and
        Zope PropertyManager requires that object properties be class attrs. So
        we need to convert certain of our inherited attrs into class attrs.
        """
        cls = self.__class__
        attrs = [p['id'] for p in cls._properties]
        for attr in attrs:
            # don't need values here since they are overriden by instance attrs
            cls.__dict__[attr] = None


    ##
    # Management methods
    ##

    security.declarePublic('index_html')
    index_html = PageTemplateFile('www/manage_test.pt', globals())

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