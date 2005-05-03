from Products.FCKeditor.FCKeditor import FCKexception
from Products.FCKeditor.FCKconnector import FCKconnector

# Zope
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products import meta_types


class ZopeFCKconnector(FCKconnector):
    """This class provides back-end integration for FCKeditor's file browser.

    Please see the FCKeditor documentation for more information.

    """

    security = ClassSecurityInfo()
    # We use restrictedTraverse to delegate security responsibility to other
    # objects

    RESPONSE_TEMPLATE = """\
    <?xml version="1.0" encoding="utf-8" ?>
        <Connector command="%(RequestedCommandName)s"
                   resourceType="%(RequestedResourceType)s">
        <CurrentFolder path="%(CurrentFolderPath)s"
                       url="%(CurrentFolderUrl)s" />
        <!-- Here goes all specific command data -->
        %(CommandData)s
    </Connector>"""

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
        return method(ResourceType, FolderPath, ServerPath)

    security.declarePrivate('_validate')

    security.declarePrivate('GetFolders')
    def GetFolders(self, ResourceType, FolderPath, ServerPath):
        """Get the list of the children folders of a folder."""
        folder = self.restrictedTraverse(FolderPath)
        return

    security.declarePrivate('GetFoldersAndFiles')
    def GetFoldersAndFiles(self, ResourceType, FolderPath, ServerPath):
        """Gets the list of the children folders and files of a folder."""
        pass

    security.declarePrivate('CreateFolder')
    def CreateFolder(self, ResourceType, FolderPath, ServerPath):
        """Create a child folder."""
        pass

    security.declarePrivate('FileUpload')
    def FileUpload(self, ResourceType, FolderPath, ServerPath):
        """Add a file in a folder."""
        pass
