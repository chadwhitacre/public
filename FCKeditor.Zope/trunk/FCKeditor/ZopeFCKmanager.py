# python
import re

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

    Specific services provided include:

        - creation of on-the-fly FCKeditor objects, with rule-based
          configuration

        - a backend for the FCKeditor file browser

    """

    security = ClassSecurityInfo()

    id = ''
    title = ''
    meta_type = 'FCKmanager'

    # these properties map FCKeditor ResourceType to Zope meta_type
    FolderTypes = ('Folder',)
    FileTypes = ('File',)
    ImageTypes = ('Image',)
    FlashTypes = ()
    MediaTypes = ()

    _properties=( { 'id':'title', 'type':'string', 'mode':'w' }
                , { 'id':'FolderTypes', 'type':'lines', 'mode':'w' }
                , { 'id':'FileTypes', 'type':'lines', 'mode':'w' }
                , { 'id':'ImageTypes', 'type':'lines', 'mode':'w' }
                , { 'id':'FlashTypes', 'type':'lines', 'mode':'w' }
                , { 'id':'MediaTypes', 'type':'lines', 'mode':'w' }
                  )

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

    security.declarePublic('connect')
    def connector(self, REQUEST):
        """REQUEST acts like a dict, so we could hand it directly to our
        superclass. However, we need to set response headers based on
        Command, so we end up overriding.

        """

        data = self._validate(REQUEST)
        Command = data['Command']
        if Command in ( 'GetFolders'
                      , 'GetFoldersAndFiles'
                      , 'CreateFolder'
                           ):
            REQUEST.RESPONSE.setHeader('Content-Type', 'text/xml')
            REQUEST.RESPONSE.setHeader('Cache-Control', 'no-cache')

        if hasattr(self, Command):
            method = getattr(self, Command)
            return method(**data)
        else:
            return ''

    security.declarePrivate('_validate')
    def _validate(self, incoming):
        """Extend the base class to override ServerPath.
        """
        outgoing = FCKconnector._validate(self, incoming)
        del outgoing['ServerPath']
        return outgoing

    security.declarePrivate('_FCK2Zope')
    def _FCK2Zope(self, Type):
        """Given an FCKeditor ResourceType, return a list of Zope meta_types.
        """
        propname = Type + 'Types'
        if not hasattr(self, propname):
            raise FCKexception, "Property '%s' does not exist" % propname
        return getattr(self, propname)


    ##
    # Command support
    ##

    security.declarePrivate('GetFolders')
    def GetFolders(self, Type, CurrentFolder, **other):
        """Get the list of the children folders of a folder."""

        folder = self.restrictedTraverse('..'+CurrentFolder)

        meta_types = self._FCK2Zope('Folder')
        folders = folder.objectIds(meta_types)

        xml_response = self._xmlGetFolders( Type
                                          , CurrentFolder
                                          , CurrentFolder # ServerPath
                                          , folders
                                           )
        return xml_response




    security.declarePrivate('GetFoldersAndFiles')
    def GetFoldersAndFiles(self, Type, CurrentFolder, **other):
        """Gets the list of the children folders and files of a folder."""

        folder = self.restrictedTraverse('..'+CurrentFolder)

        meta_types = self._FCK2Zope('Folder')
        folders = folder.objectIds(meta_types)

        meta_types = self._FCK2Zope(Type)
        files = [self._file_info(f) for f in folder.objectValues(meta_types)]

        xml_response = self._xmlGetFoldersAndFiles( Type
                                                  , CurrentFolder
                                                  , CurrentFolder # ServerPath
                                                  , folders
                                                  , files
                                                   )
        return xml_response

    security.declarePrivate('_get_info')
    def _get_info(self, o, t):
        """Given a tuple, return a value."""
        for attr in t:
            if hasattr(o, attr):
                attr = getattr(o, attr)
                break
            else:
                attr = None
        if callable(attr):
            value = attr()
        else:
            value = attr
        return value

    security.declarePrivate('_file_info')
    def _file_info(self, f):
        """Given an object, return a tuple."""

        id = self._get_info(f, ('getId','id'))
        size = self._get_info(f, ('getSize','get_size'))
        size = size / 1024 # convert to kB

        return (id, size)



    security.declarePrivate('CreateFolder')
    _bad_id=re.compile(r'[^a-zA-Z0-9-_~,.$\(\)# ]').search
    def CreateFolder(self, Type, CurrentFolder, NewFolderName, **other):
        """Create a child folder."""

        folder = self.restrictedTraverse('..'+CurrentFolder)

        if hasattr(folder, NewFolderName):
            error_code = 101 # Folder already exists.
        elif self._bad_id(NewFolderName) is not None:
            error_code = 102 # Invalid folder name.
        elif 0:
            error_code = 103 # You have no permissions to create the folder.
        else:
            try:
                # We are lazy and assume that folder objects know how to
                # replicate themselves.
                folder.manage_addFolder(NewFolderName)
                error_code = 0 # No Errors Found. The folder has been created.
            except:
                error_code = 110 # Unknown error creating folder.

        xml_response = self._xmlCreateFolder( Type
                                            , CurrentFolder
                                            , CurrentFolder # ServerPath
                                            , error_code
                                             )

        return xml_response




    security.declarePrivate('FileUpload')
    def FileUpload(self, Type, CurrentFolder, NewFile, **other):
        """Add a file in a folder."""

        # disable this feature for now
        html_response = self._htmlCreateFolder( Type
                                              , CurrentFolder
                                              , 202
                                              )

        folder = self.restrictedTraverse('..'+CurrentFolder)

        filename = NewFile.filename

        if self._bad_id(filename) is not None:
            error_code = 202 # invalid file.

        elif hasattr(folder, filename):
            # FCKeditor spec calls for renaming the file in this case

            parts = filename.split('.')

            def _new_filename(parts, i):
                if len(parts) == 1:
                    parts.append('(%s)' % i)
                elif len(parts) > 1:
                    parts.insert(-1,'(%s)' % i)
                else: # parts < 1
                    raise FCKexception, "Should never get here"
                return ''.join(parts)

            i = 0
            while hasattr(folder, filename):
                i += 1
                filename = _new_filename(parts, i)

        else:
            try:
                # We want to create the first type in the list.
                folder.manage_addFile(filename, NewFile)
                error_code = 0 # No Errors Found. The folder has been created.
            except:
                error_code = 110 # Unknown error creating folder.

        html_response = self._htmlCreateFolder( Type
                                              , CurrentFolder
                                              , error_code
                                              )

        return html_response

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