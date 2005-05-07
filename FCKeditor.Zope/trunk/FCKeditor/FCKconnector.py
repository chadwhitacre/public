from FCKeditor import FCKexception

class FCKconnector:
    """This class provides back-end integration for FCKeditor's file browser.

    As it stands this class is not useable, and it will need to be extended by
    framework wrappers in the following ways:

        - override connector to set the response headers as necessary

        - override the GetFolders, GetFoldersAndFiles, CreateFolder, and
          FileUpload methods to provide actual logic. These methods should call
          their _[x|ht]ml* complements to properly format the response body.

    Please see the FCKeditor documentation and ZopeFCKconnector.py for
    documentation and an example wrapper.

    """

    def connector(self, incoming):
        """Given a dictionary, validate it and hand it off to another method.

        This is the main callable and should be overridden or extended by
        framework wrappers as necessary. FCKeditor sends us a querystring with
        up to five parameters in it. A sixth parameter may be given in the post:

            Command         required    string
            CurrentFolder   required    string
            Type            required    string
            ServerPath      optional    string
            NewFolderName   optional    string
            NewFile         optional    object

        After validating our input into a dictionary, we hand this off to a
        method matching the name given as Command.

        """
        data = incoming # in wrapper, parse input out of the querystring
        data = self._validate(data) # will raise an error if bad data
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

        NewFolderName = incoming.get('NewFolderName', '') # optional

        NewFile = incoming.get('NewFile', None) # optional

        ServerPath = incoming.get('ServerPath', '')
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

        FCKeditor docs call for providing server-side config of ServerPath. If
        this is desired then override this method in your framework wrapper.

        """
        ServerPath = ServerPath # server-side config is framework-specific
        if ServerPath == '':
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

    def _xmlGetFolders(self, Type, CurrentFolder, ComputedUrl, Folders):
        """Given three strings and a list, format an XML response.
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

        return template % (Type, CurrentFolder, ComputedUrl, folders)




    def GetFoldersAndFiles(self, **kw):
        """Gets the list of the children folders and files of a folder."""
        pass

    def _xmlGetFoldersAndFiles(self, Type, CurrentFolder, ComputedUrl,
                               Folders, Files):
        """Given three strings and two lists, format an XML response.
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

        return template % (Type, CurrentFolder, ComputedUrl, folders, files)




    def CreateFolder(self, **kw):
        """Create a child folder."""
        pass

    def _xmlCreateFolder(self, Type, CurrentFolder, ComputedUrl, error_code):
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

    def _htmlFileUpload(self, error_code):
        """Given a string, format an XML response.
        """

        template = """\
<script type="text/javascript">
    window.parent.frames['frmUpload'].OnUploadCompleted(%s) ;
</script>"""

        return template % error_code