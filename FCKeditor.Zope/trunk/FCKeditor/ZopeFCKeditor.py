# python
import re

# Zope
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# us
from FCKeditor import FCKeditor, FCKexception
MANAGE_PERM = 'Manage FCKeditor'

class ZopeFCKeditor(FCKeditor, PropertyManager, SimpleItem):
    """A Zope wrapper around FCKeditor.

    Usage ideas:

        1. Multiple instances could be used to store a particular FCKeditor
        configuration

        2. Could be subclassed by a content object

        3. Can be used on the fly via ZopeFCKmanager

    """

    security = ClassSecurityInfo()

    # security declarations for base class API
    security.declarePrivate('_bad_chars')
    security.declarePrivate('_scrub')
    security.declarePublic('Create')
    security.declarePrivate('_config2querystring')
    security.declarePrivate('_parse_dimensions')
    security.declareProtected(MANAGE_PERM, 'SetCompatible')

    id = ''
    title = ''
    meta_type = 'FCKeditor'

    _properties = ( {'id':'title',          'type':'string', 'mode':'w'}
                  , {'id':'InstanceName',   'type':'string', 'mode':'w'}
                  , {'id':'Width',          'type':'string', 'mode':'w'}
                  , {'id':'Height',         'type':'string', 'mode':'w'}
                  , {'id':'ToolbarSet',     'type':'string', 'mode':'w'}
                  , {'id':'Value',          'type':'string', 'mode':'w'}
                  , {'id':'BasePath',       'type':'string', 'mode':'w'}
                   )

    manage_options = PropertyManager.manage_options +\
                     ({'label':'View', 'action':''},) +\
                     SimpleItem.manage_options

    def __init__(self, id, title=''):
        # set basic props
        self.id = id
        self.title = title

        # InstanceName should default to id
        kw['InstanceName'] = id

        # final initialization
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
            # We don't actually need values here since they are overriden by
            # the instance attrs.
            cls.__dict__[attr] = ''


    security.declareProtected(MANAGE_PERM, 'SetConfig')
    def SetConfig(self, key, val):
        """support configuration
        """
        self.config[key] = val


    ##
    # Management methods
    ##

    security.declarePublic('index_html')
    index_html = PageTemplateFile('www/manage_test.pt', globals())

InitializeClass(ZopeFCKeditor)



##
# Product addition and registration
##

addForm = PageTemplateFile('www/addFCKeditor.pt', globals())

def manage_addFCKeditor(self, id, title='', REQUEST=None):
    """  """
    self._setObject(id, ZopeFCKeditor(id, title))
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

def initialize(context):
    context.registerClass(
        ZopeFCKeditor,
        permission='Add FCKeditor',
        constructors=( addForm, manage_addFCKeditor ),
        icon='www/fckeditor.gif',
        )