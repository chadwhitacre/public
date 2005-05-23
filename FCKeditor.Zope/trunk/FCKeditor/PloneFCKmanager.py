# Zope
from AccessControl import ClassSecurityInfo, Unauthorized
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.utils import UniqueObject

# us
from Products.FCKeditor.FCKconnector import FCKconnector
from Products.FCKeditor.ZopeFCKeditor import ZopeFCKeditor

# constants
LIST = 'List folder contents'
VIEW = 'View'
ID = 'portal_fckmanager'


class PloneFCKmanager(FCKconnector, UniqueObject, PropertyManager, SimpleItem):
    """A Plone tool to support FCKeditor objects.
    """

    security = ClassSecurityInfo()

    id = ID
    title = 'Manage a set of FCKeditors'
    meta_type = 'FCKmanager for Plone'

    manage_options = PropertyManager.manage_options +\
                     SimpleItem.manage_options

    def __init__(self, id, title=''):
        self.id = id
        self.title = title

    security.declarePublic('spawn')
    def spawn(self, id):
        """Given an id string, return an FCKeditor object.
        """
        return ZopeFCKeditor(id)

    security.declarePublic('connector')
    def connector(self, REQUEST):

        """REQUEST acts like a dict, so we could hand it directly to our
        superclass. However, we need to set response headers based on Command,
        so we end up overriding. We also stick the user in there so we can
        perform security checks against it.

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

        logic_method = getattr(self, Command)
        data.update(logic_method(**data))

        response_method = getattr(self, '%s_response' % Command)
        return response_method(**data)

    def _compute_url(self, ServerPath, Type, CurrentFolder, **other):
        """We depart from the FCK spec at this point because we don't want
        to organize our content in ResourceType folders.

        """
        return CurrentFolder


    ##
    # Command support
    ##

    security.declarePrivate('GetFolders')
    def GetFolders(self, Type, CurrentFolder, ComputedUrl, User, **other):
        """Get the list of the children folders of a folder."""

        folder = self.unrestrictedTraverse('..'+CurrentFolder)
        if not User.has_permission(LIST, folder):
            folders = []
        else:
            folders = folder.objectValues('Plone Folder')
            folders = [o.getId() for o in folders if User.has_permission(
                                                      LIST, o)]

        return { 'folders' : folders }



    security.declarePrivate('GetFoldersAndFiles')
    def GetFoldersAndFiles(self, Type, CurrentFolder, ComputedUrl, User,
                           **other):
        """Gets the list of the children folders and files of a folder."""

        folder = self.unrestrictedTraverse('..'+CurrentFolder)
        if not User.has_permission(LIST, folder):
            # return an empty page if no permissions
            folders = files = []
        else:
            # get folders
            folders = folder.objectValues('Plone Folder')
            folders = [o.getId() for o in folders
                                       if User.has_permission(LIST, o)]

            # get files
            # map FCK Type to Zope meta_type
            if Type == 'Image':
                meta_types = ('Portal Image',)
            else:
                meta_types = ('Portal File','Document')

            files = folder.objectValues(meta_types)
            files = [self._file_info(o) for o in files
                                              if User.has_permission(VIEW, o)]

        return { 'folders' : folders
               , 'files'   : files
                }

    security.declarePrivate('_file_info')
    def _file_info(o):
        """Given an object, return a tuple."""

        id = o.getId()
        size = o.getSize()
        size = size / 1024 # convert to kB

        return (id, size)
    _file_info = staticmethod(_file_info)

    #security.declarePrivate('_get_info')
    #def _get_info(self, o, t):
    #    """Given an object and tuple of strings, return a value."""
    #    for attr in t:
    #        if getattr(o, attr, None) is not None:
    #            attr = getattr(o, attr)
    #            break
    #        else:
    #            attr = None
    #    if callable(attr):
    #        value = attr()
    #    else:
    #        value = attr
    #    return value




    security.declarePrivate('CreateFolder')
    def CreateFolder(self, Type, CurrentFolder, NewFolderName, ComputedUrl,
                     **other):
        """Create a child folder."""

        folder = self.unrestrictedTraverse('..'+CurrentFolder)

        if NewFolderName in folder.contentIds():
            error_code = 101 # Folder already exists.
        elif folder.check_id(NewFolderName) is not None:
            error_code = 102 # Invalid folder name.
        else:
            try:
                # get the constructor via traversal so that we trigger security
                constructor = folder.restrictedTraverse('invokeFactory')
                constructor('Folder', NewFolderName)
                error_code = 0 # No Errors Found. The folder has been created.
            except Unauthorized:
                error_code = 103 # You have no permissions to create the folder.
            except:
                error_code = 110 # Unknown error creating folder.

        return { 'error_code' : error_code }



    def FileUpload(self, **kw):
        """Add a file in a folder."""
        #return { 'error_code' : 202 }
        raise NotImplemented, "sorry, not done yet"


InitializeClass(PloneFCKmanager)



##
# Product addition and registration
##

def manage_addPloneFCKmanager(self, REQUEST=None):
    """  """
    self._setObject(ID, PloneFCKmanager(ID))
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

def initialize(context):
    context.registerClass(
        PloneFCKmanager,
        permission='Add FCKmanager for Plone',
        constructors=(manage_addPloneFCKmanager,),
        icon='www/fckmanager.gif',
        )
