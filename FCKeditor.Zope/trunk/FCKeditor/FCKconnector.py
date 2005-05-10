from Products.FCKeditor import FCKexception

class FCKconnector:
    """This class provides back-end integration for FCKeditor's file browser.

    The pattern anticipated in this class is that all public calls will go to
    the connector method. Connector will marshall the incoming HTTP get/post
    into a dictionary, which it will run through _validate. After validating our
    input into another dictionary, connector will hand this off to a method
    matching the name given as Command.

    <Command> -- which are just stubs in this class because their implementation
    is framework-dependent -- will extract the input it needs from the incoming
    dictionary, and will return an xml or html snippet to return to the
    FCKeditor File Browser. Marshalling the result into an xml or html response
    is framework independent, so that particular functionality is factored out
    into separate methods.

    """

    __all__ = ('connector',)

    def connector(self, incoming):
        """Given a dictionary, validate it and hand it off to another method.

        This is the main callable and should be overridden or extended by
        framework wrappers as necessary. FCKeditor sends us a querystring or a
        post with up to six parameters in it:

            Command         required    string
            CurrentFolder   required    string
            NewFile         optional    object
            NewFolderName   optional    string
            ServerPath      optional    string
            Type            required    string

        """
        data = incoming # in wrapper, parse input out of the querystring
        data = self._validate(data) # will raise an FCKexception if bad data

        # You will also need to set the HTTP response headers appropriately
        # based on whether we are returning XML or HTML content.

        method = getattr(self, data['Command'])
        return method(**data)

    def _validate(self, incoming):
        """Given a dictionary, return a validated dict.
        """

        # Parse our six variables out of the dict and validate them.
        # A seventh dict key is computed.

        Command = incoming.get('Command', '')
        if getattr(self, Command, None) is None:
            raise FCKexception, "Command '%s' not found" % Command

        CurrentFolder = incoming.get('CurrentFolder', '')
        if not (( CurrentFolder.startswith('/') and
                  CurrentFolder.endswith('/')
                   )):
            raise FCKexception, "CurrentFolder '%s' must" % CurrentFolder +\
                                " start and end with a forward slash."

        NewFile = incoming.get('NewFile', None) # optional

        NewFolderName = incoming.get('NewFolderName', '') # optional

        ServerPath = incoming.get('ServerPath', None)
        if ServerPath: # optional
            if not (ServerPath.startswith('/') and ServerPath.endswith('/')):
                raise FCKexception, "ServerPath '%s' must" % ServerPath +\
                                    " start and end with '/'"

        Type = incoming.get('Type', '')
        if Type not in ( 'File'
                       , 'Image'
                       , 'Flash'
                       , 'Media'
                        ):
            raise FCKexception, "Type '%s' not found" % Type

        ComputedUrl = self._compute_url(ServerPath, Type, CurrentFolder)

        return { 'Command'       : Command
               , 'ComputedUrl'   : ComputedUrl
               , 'CurrentFolder' : CurrentFolder
               , 'NewFolderName' : NewFolderName
               , 'NewFile'       : NewFile
               , 'ServerPath'    : ServerPath
               , 'Type'          : Type
                }

    def _compute_url(self, ServerPath, Type, CurrentFolder, **other):
        """Given three strings, compute the FCK url path

        FCKeditor docs call for storing files in a particular hierarchy. They
        also call for providing server-side config of ServerPath. If this is
        desired then override this method in your framework wrapper.

        Validation of input is the responsibility of the caller.

        """
        ServerPath = ServerPath # server-side config is framework-specific
        if ServerPath is None:
            ServerPath = '/UserFiles/'
        return ServerPath + Type + CurrentFolder


    def GetFolders(self, **kw):
        """Get the list of the children folders of a folder."""
        # here is an example of what these four methods should do:

        # folders = get list of folder names per your framework

        # response_body = self._xmlGetFolders( Type, CurrentFolder
        #                                    , ServerPath, folders)

        # return response_body

        pass

    def GetFolders_response(self, Type, CurrentFolder, ComputedUrl, folders,
                            **other):
        """Given three strings and a list, format an XML response.
        """

        folder_template = '''<Folder name="%s" />'''
        folders_xml = '\n      '.join([folder_template % f for f in folders])

        template = """\
<?xml version="1.0" encoding="utf-8" ?>
  <Connector command="GetFolders" resourceType="%s">
    <CurrentFolder path="%s" url="%s" />
    <Folders>
      %s
    </Folders>
</Connector>"""

        return template % (Type, CurrentFolder, ComputedUrl, folders_xml)




    def GetFoldersAndFiles(self, **kw):
        """Gets the list of the children folders and files of a folder."""
        pass

    def GetFoldersAndFiles_response(self, Type, CurrentFolder, ComputedUrl,
                               folders, files, **other):
        """Given three strings and two lists, format an XML response.
        """

        # folders just needs to be a list of names
        folder_template = '''<Folder name="%s" />'''
        folders_xml = '\n      '.join([folder_template % f for f in folders])

        # files needs to be a list of (name, size) tuples; size is kB
        file_template = '''<File name="%s" size="%s" />'''
        files_xml   = '\n      '.join([file_template % f for f in files])

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

        return template % (Type, CurrentFolder, ComputedUrl, folders_xml,
                           files_xml)




    def CreateFolder(self, **kw):
        """Create a child folder."""
        pass

    def CreateFolder_response(self, Type, CurrentFolder, ComputedUrl, error_code,
                              **other):
        """Given four strings, format an XML response.
        """

        template = """\
<?xml version="1.0" encoding="utf-8" ?>
  <Connector command="CreateFolder" resourceType="%s">
    <CurrentFolder path="%s" url="%s" />
    <Error number="%s" />
</Connector>"""

        return template % (Type, CurrentFolder, ComputedUrl, error_code)




    def FileUpload(self, **kw):
        """Add a file in a folder."""
        pass

    def FileUpload_response(self, error_code, **other):
        """Given a string, format an XML response.
        """

        template = """\
<script type="text/javascript">
    window.parent.frames['frmUpload'].OnUploadCompleted(%s) ;
</script>"""

        return template % error_code