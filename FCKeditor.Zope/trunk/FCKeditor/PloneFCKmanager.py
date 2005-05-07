# base classes
from Products.FCKeditor.ZopeFCKmanager import ZopeFCKmanager
from Products.CMFCore.utils import UniqueObject

# Zope
from AccessControl import ClassSecurityInfo, Unauthorized
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

ID = 'portal_fckmanager'

class PloneFCKmanager(ZopeFCKmanager, UniqueObject):
    """A Plone tool to support FCKeditor objects.
    """

    id = ID
    title = 'Manage a set of FCKeditors'
    meta_type = 'FCKmanager for Plone'

    security = ClassSecurityInfo()

    security.declarePrivate('GetFolders')
    def GetFolders(self, Type, CurrentFolder, ComputedUrl, **other):
        """Override to use Plone types and logic."""
        folder = self.restrictedTraverse('..'+CurrentFolder)
        folders = folder.objectIds(('Plone Folder', 'Large Plone Folder'))
        xml_response = self._xmlGetFolders( Type
                                          , CurrentFolder
                                          , ComputedUrl
                                          , folders
                                           )
        return xml_response

    security.declarePrivate('GetFoldersAndFiles')
    def GetFoldersAndFiles(self, Type, CurrentFolder, ComputedUrl, **other):
        """Override to use Plone types and logic."""
        folder = self.restrictedTraverse('..'+CurrentFolder)
        folders = folder.contentIds(('Plone Folder', 'Large Plone Folder'))

        image = Type == 'Image'
        meta_types = image and 'Portal Image' or ('Portal File', 'Document')
        files = [self._file_info(f) for f in folder.objectValues(meta_types)]

        xml_response = self._xmlGetFoldersAndFiles( Type
                                                  , CurrentFolder
                                                  , ComputedUrl
                                                  , folders
                                                  , files
                                                   )
        return xml_response

    security.declarePrivate('CreateFolder')
    def CreateFolder(self, Type, CurrentFolder, NewFolderName, ComputedUrl,
                     **other):
        """Override to use Plone types and logic."""

        folder = self.restrictedTraverse('..'+CurrentFolder)

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
                raise
                error_code = 110 # Unknown error creating folder.

        xml_response = self._xmlCreateFolder( Type
                                            , CurrentFolder
                                            , ComputedUrl
                                            , error_code
                                             )

        return xml_response


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
        icon='www/fckmanager-plone.gif',
        )