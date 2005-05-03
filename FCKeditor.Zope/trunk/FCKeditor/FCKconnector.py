from FCKeditor import FCKexception

class FCKconnector:
    """This class provides back-end integration for FCKeditor's file browser.

    Framework wrappers will need to extend the connect method and override the
    others. Please see the FCKeditor documentation and ZopeFCKconnector.py for
    documentation and an example wrapper.

    """

    RESPONSE_TEMPLATE = """\
    <?xml version="1.0" encoding="utf-8" ?>
        <Connector command="%(RequestedCommandName)s"
                   resourceType="%(RequestedResourceType)s">
        <CurrentFolder path="%(CurrentFolderPath)s"
                       url="%(CurrentFolderUrl)s" />
        <!-- Here goes all specific command data -->
        %(CommandData)s
    </Connector>"""

    def connect(self, incoming):
        """Given a dictionary, validate it and hand it off to another method.

        This is the main callable and should be overridden or extended by
        framework wrappers as necessary.

        """
        data = self._validate(incoming) # will raise an error if bad data
        method = getattr(self, data['CommandName'])
        return method(ResourceType, FolderPath, ServerPath)

    def _validate(self, incoming):
        """Given a dictionary, return a validated dict.
        """

        # parse our four variables out of the dict and validate them

        CommandName  = incoming.get('CommandName', '')
        if not hasattr(self, CommandName):
            raise FCKexception, "CommandName '%s' not found" % CommandName

        ResourceType = incoming.get('ResourceType', '')
        if ResourceType not in ( ''
                               , 'File'
                               , 'Image'
                               , 'Flash'
                               , 'Media'
                                ):
            raise FCKexception, "ResourceType '%s' not found" % ResourceType

        FolderPath   = incoming.get('FolderPath', '')
        if not (FolderPath.startswith('/') and FolderPath.endswith('/')):
            raise FCKexception, "FolderPath '%s' must" % FolderPath +\
                                " start and end with '/'"

        ServerPath   = incoming.get('ServerPath', '')
        if not (ServerPath.startswith('/') and ServerPath.endswith('/')):
            raise FCKexception, "ServerPath '%s' must" % ServerPath +\
                                " start and end with '/'"

        return { 'CommandName'  : CommandName
               , 'ResourceType' : ResourceType
               , 'FolderPath'   : FolderPath
               , 'ServerPath'   : ServerPath
                }

    def GetFolders(self, ResourceType, FolderPath, ServerPath):
        """Get the list of the children folders of a folder."""
        pass # expects XML response

    def GetFoldersAndFiles(self, ResourceType, FolderPath, ServerPath):
        """Gets the list of the children folders and files of a folder."""
        pass # expects XML response

    def CreateFolder(self, ResourceType, FolderPath, ServerPath):
        """Create a child folder."""
        pass # expects XML response

    def FileUpload(self, ResourceType, FolderPath, ServerPath):
        """Add a file in a folder."""
        pass # expects HTML response
