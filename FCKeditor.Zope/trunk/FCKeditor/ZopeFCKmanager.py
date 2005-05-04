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
from Products.FCKeditor.ZopeFCKeditor import ZopeFCKeditor


class ZopeFCKmanager(FCKconnector, PropertyManager, SimpleItem):
    """This object provides Zope support services for FCKeditor.

    Specific services provided include creation of on-the-fly FCKeditor
    objects, and a backend for the FCKeditor file browser.

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


    security.declarePublic('connect')
    def connect(self, REQUEST):
        """REQUEST acts like a dict, so we could hand it directly to our
        superclass. However, we need to set response headers based on
        CommandName, so we end up overriding.

        """

        data = self._validate(REQUEST)
        CommandName = data['CommandName']
        if CommandName in ( 'GetFolders'
                          , 'GetFoldersAndFiles'
                          , 'CreateFolder'
                           ):
            REQUEST.RESPONSE.set('Content-Type', 'text/xml')
            REQUEST.RESPONSE.set('Cache-Control', 'no-cache')

        method = getattr(self, CommandName)
        return method(ResourceType, FolderPath)

    security.declarePrivate('_validate')
    def _validate(self, incoming):
        """Extend the base class to override ServerPath.
        """
        outgoing = FCKconnector._validate(self, incoming)
        del outgoing['ServerPath']
        return outgoing


    ##
    # CommandName support
    ##

    security.declarePrivate('GetFolders')
    def GetFolders(self, ResourceType, FolderPath):
        """Get the list of the children folders of a folder."""
        folder = self.restrictedTraverse(FolderPath[1:])
        folders = folder.objectIds('Folder')
        xml_response = self._xmlGetFolders( ResourceType
                                          , FolderPath
                                          , FolderPath # ServerPath
                                          , folders
                                           )
        return xml_response

    security.declarePrivate('GetFoldersAndFiles')
    def GetFoldersAndFiles(self, ResourceType, FolderPath):
        """Gets the list of the children folders and files of a folder."""

        folder = self.restrictedTraverse(FolderPath[1:])
        folders = folder.objectIds('Folder')
        files = [(f.getId(), (f.getSize()/1024)) for f in folder.objectValues('File')]

        xml_response = self._xmlGetFoldersAndFiles( ResourceType
                                                  , FolderPath
                                                  , FolderPath # ServerPath
                                                  , folders
                                                  , files
                                                   )
        return xml_response

    security.declarePrivate('CreateFolder')
    def CreateFolder(self, ResourceType, FolderPath, ServerPath):
        """Create a child folder."""
        pass

    security.declarePrivate('FileUpload')
    def FileUpload(self, ResourceType, FolderPath, ServerPath):
        """Add a file in a folder."""
        pass

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