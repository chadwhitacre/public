# python
import re

# base classes
from OFS.SimpleItem import SimpleItem
from OFS.ObjectManager import ObjectManager
from OFS.PropertyManager import PropertyManager

# Zope
import Products
from AccessControl import ClassSecurityInfo, Unauthorized
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products import meta_types
from zExceptions import BadRequest

# us
from Products.FCKeditor.FCKeditor import FCKexception
from Products.FCKeditor.FCKconnector import FCKconnector
from Products.FCKeditor.ZopeFCKeditor import ZopeFCKeditor

# permissions
LIST_FOLDER_CONTENTS = 'List folder contents'
VIEW = 'View'


class ZopeFCKmanager(FCKconnector, PropertyManager, SimpleItem):
    """This object provides Zope support services for FCKeditor.

    Specific services provided include:

        - creation of on-the-fly FCKeditor objects

        - a backend for the FCKeditor file browser


    Design re: *Types properties:

        So the question is: how do I get from meta_type, which is a
        property that all Zope objects are required to have -- how do I
        get from that to the object's constructor. I mean it's true
        constructor, not just the form. BUT, I need it's TTW constructor
        so that I can traverse to it and trigger security. Otherwise I
        am looking at reimplementing security.

        So the tradeoff is between implementing our own security and
        getting at the true TTW constructor.

        Of course, all of this is necessary because we are trying to
        support mapping of FCK Type to arbitrary Zope/CMF types.

        If we require that the constructor be explicitly specified along
        with the type, then we get out of discovering it ourselves.
        Since discovery appears to be a big pain, and the type mapping
        is an admin-level thing anyway, and this is only version 1, that
        is what we'll do.

    """

    security = ClassSecurityInfo()

    id = ''
    title = ''
    meta_type = 'FCKmanager'

    # these properties map FCKeditor ResourceType to Zope meta_type
    # the value is a tuple of (meta_type, constructory) two-tuples
    FolderTypes = (('Folder','manage_addFolder'),)
    FileTypes = (('File','manage_addFile'),)
    ImageTypes = (('Image','manage_addImage'),)
    FlashTypes = ()
    MediaTypes = ()

    _properties=( { 'id':'title',       'type':'string',    'mode':'w' }
                , { 'id':'FolderTypes', 'type':'lines',     'mode':'w' }
                , { 'id':'FileTypes',   'type':'lines',     'mode':'w' }
                , { 'id':'ImageTypes',  'type':'lines',     'mode':'w' }
                , { 'id':'FlashTypes',  'type':'lines',     'mode':'w' }
                , { 'id':'MediaTypes',  'type':'lines',     'mode':'w' }
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

    security.declarePublic('connector')
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

        data['User'] = REQUEST.get('AUTHENTICATED_USER')

        if getattr(self, Command, None) is not None:
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

    def _compute_url(self, ServerPath, Type, CurrentFolder, **other):
        """We depart from the FCK spec at this point because we don't want
        to organize our content that way.

        """
        return CurrentFolder



    ##
    # Command support
    ##

    security.declarePrivate('GetFolders')
    def GetFolders(self, Type, CurrentFolder, ComputedUrl, User, **other):
        """Get the list of the children folders of a folder."""

        folder = self.unrestrictedTraverse('..'+CurrentFolder)
        if not User.has_permission(LIST_FOLDER_CONTENTS, folder):
            folders = []
        else:
            folders = [o.getId() for o in folder.objectValues('Folder')
                               if User.has_permission(LIST_FOLDER_CONTENTS, o)]

        xml_response = self._xmlGetFolders( Type
                                          , CurrentFolder
                                          , ComputedUrl
                                          , folders
                                           )
        return xml_response




    security.declarePrivate('GetFoldersAndFiles')
    def GetFoldersAndFiles(self, Type, CurrentFolder, ComputedUrl, User, **other):
        """Gets the list of the children folders and files of a folder."""

        folder = self.unrestrictedTraverse('..'+CurrentFolder)
        if not User.has_permission(LIST_FOLDER_CONTENTS, folder):
            # if the user doesn't have permission on this folder, return an empty
            # page
            folders = files = []
        else:
            folder = self.unrestrictedTraverse('..'+CurrentFolder)
            folders = [o.getId() for o in folder.objectValues('Folder')
                               if User.has_permission(LIST_FOLDER_CONTENTS, o)]

            if Type == 'Image':
                meta_type = 'Image'
            else:
                meta_type = 'File'

            files = [self._file_info(o) for o in folder.objectValues(meta_types)
                                              if User.has_permission(VIEW, o)]

        xml_response = self._xmlGetFoldersAndFiles( Type
                                                  , CurrentFolder
                                                  , ComputedUrl
                                                  , folders
                                                  , files
                                                   )
        return xml_response

    security.declarePrivate('_get_info')
    def _get_info(self, o, t):
        """Given a tuple, return a value."""
        for attr in t:
            if getattr(o, attr, None) is not None:
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
    def CreateFolder(self, Type, CurrentFolder, NewFolderName, ComputedUrl,
                     **other):
        """Create a child folder."""

        folder = self.restrictedTraverse('..'+CurrentFolder)

        error_code = 110
        if NewFolderName in folder.objectIds():
            error_code = 101 # Folder already exists.
        else:
            try:
                folder._checkId(NewFolderName)
            except BadRequest:
                error_code = 102 # Invalid folder name.

        if error_code == 110:
            try:
                # get the constructor via traversal so that we trigger security
                constructor = folder.restrictedTraverse('manage_addFolder')
                constructor(NewFolderName)
                error_code = 0 # No Errors Found. The folder has been created.
            except Unauthorized:
                error_code = 103 # You have no permissions to create the folder.
            except:
                error_code = 110 # Unknown error creating folder.

        xml_response = self._xmlCreateFolder( Type
                                            , CurrentFolder
                                            , ComputedUrl
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
        return html_response

        folder = self.restrictedTraverse('..'+CurrentFolder)
        filename = NewFile.filename

        error_code = 110
        try:
            self._checkId(filename)
        else:
            error_code = 202 # invalid file.

        if
        elif getattr(folder, filename, None) is not None:
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
            while getattr(folder, filename, None) is not None:
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