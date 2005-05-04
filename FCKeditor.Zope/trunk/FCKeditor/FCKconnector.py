from FCKeditor import FCKexception

class FCKconnector:
    """This class provides back-end integration for FCKeditor's file browser.

    As it stands this class is not useable, and it will need to be extended by
    framework wrappers in the following ways:

        - override connect to set the response headers as necessary

        - override the GetFolders, GetFoldersAndFiles, CreateFolder, and
        FileUpload methods to provide actual logic. These methods should call
        their _[x|ht]ml* equivalents to properly format the response body.

      will need to extend the connect
    method and override the others. Please see the FCKeditor documentation and
    ZopeFCKconnector.py for documentation and an example wrapper.

    """

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
        if ServerPath: # it is optional
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
        # here is an example of what these four methods should do:

        # folders = get list of folder names per your framework

        # response_body = self._xmlGetFolders( ResourceType, FolderPath
        #                                    , ServerPath, folders)

        # return response_body

        pass

    def _xmlGetFolders(self, ResourceType, FolderPath, ServerPath, Folders):
        """Given the input and a list of folders, format an XML response.
        """

        folder_template = '''<Folder name="%s" />'''
        folders = '\n      '.join([folder_template % f for f in Folders])

        template = """\
<?xml version="1.0" encoding="utf-8" ?>
  <Connector command="GetFolders" resourceType="%s">
    <CurrentFolder path="%s" url="%s" />
    <Folders>
      %s
    </Folders>
</Connector>"""

        return template % (ResourceType, FolderPath, ServerPath, folders)




    def GetFoldersAndFiles(self, ResourceType, FolderPath, ServerPath):
        """Gets the list of the children folders and files of a folder."""
        pass # expects XML response

    def _xmlGetFoldersAndFiles(self, ResourceType, FolderPath, ServerPath,
                               Folders, Files):
        """Given the input and a list of folders, format an XML response.
        """

        # folders just needs to be a list of names
        folder_template = '''<Folder name="%s" />'''
        folders = '\n      '.join([folder_template % f for f in Folders])

        # files needs to be a list of (name, size) tuples; size is kB
        file_template = '''<File name="%s" size="%s" />'''
        files   = '\n      '.join([file_template % f for f in Files])

        template = """\
<?xml version="1.0" encoding="utf-8" ?>
  <Connector command="GetFoldersAndFiles" resourceType="%s">
    <CurrentFolder path="%s" url="%s" />
    <Folders>
      %s
    </Folders>
    <Files>
      %s
    </Files>
</Connector>"""

        return template % (ResourceType, FolderPath, ServerPath, folders, files)




    def CreateFolder(self, ResourceType, FolderPath, ServerPath):
        """Create a child folder."""
        pass # expects XML response

    def _xmlGetFolders(self, ResourceType, FolderPath, ServerPath, Folders):
        """Given the input and a list of folders, format an XML response.
        """

        folder_template = '''<Folder name="%s" />'''
        folders = '\n      '.join([folder_template % f for f in Folders])

        template = """\
<?xml version="1.0" encoding="utf-8" ?>
  <Connector command="GetFolders" resourceType="%s">
    <CurrentFolder path="%s" url="%s" />
    <Folders>
      %s
    </Folders>
</Connector>"""

        return template % (ResourceType, FolderPath, ServerPath, folders)




    def FileUpload(self, ResourceType, FolderPath, ServerPath):
        """Add a file in a folder."""
        pass # expects HTML response
