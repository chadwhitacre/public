#BOILERPLATE###################################################################
#                                                                             #
#  This package wraps FCKeditor for use in the Zope web application server.   #
#  Copyright (C) 2005 Chad Whitacre <http://www.zetadev.com/>                 #
#                                                                             #
#  This library is free software; you can redistribute it and/or modify it    #
#  under the terms of the GNU Lesser General Public License as published by   #
#  the Free Software Foundation; either version 2.1 of the License, or (at    #
#  your option) any later version.                                            #
#                                                                             #
#  This library is distributed in the hope that it will be useful, but        #
#  WITHOUT ANY WARRANTY; without even the implied warranty of                 #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser    #
#  General Public License for more details.                                   #
#                                                                             #
#  You should have received a copy of the GNU Lesser General Public License   #
#  along with this library; if not, write to the Free Software Foundation,    #
#  Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA                #
#                                                                             #
###################################################################BOILERPLATE#
# Python
import re

# us
from Products.FCKeditor import FCKexception

class Templates:
    """Storage for XML and HTML templates used below.
    """

    GetFolders = """\
<?xml version="1.0" encoding="utf-8" ?>
  <Connector command="GetFolders" resourceType="%s">
    <CurrentFolder path="%s" url="%s" />
    <Folders>
      %s
    </Folders>
</Connector>"""

    GetFoldersAndFiles = """\
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

    CreateFolder = """\
<?xml version="1.0" encoding="utf-8" ?>
  <Connector command="CreateFolder" resourceType="%s">
    <CurrentFolder path="%s" url="%s" />
    <Error number="%s" />
</Connector>"""

    FileUpload = """\
<script type="text/javascript">
    window.parent.frames['frmUpload'].OnUploadCompleted(%s) ;
</script>"""


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
        data = self._validate(data) # will raise FCKexception if bad data

        # You will also need to set the HTTP response headers appropriately
        # based on whether we are returning XML or HTML content.

        method = getattr(self, data['Command'])
        return method(**data)

    def _validate(self, incoming):
        """Given a dictionary, return a validated dict.
        """

        # Parse our six variables out of the dict and validate them.
        # A seventh dict value is computed.

        Command = incoming.get('Command', '')
        if Command not in ( 'GetFolders'
                          , 'GetFoldersAndFiles'
                          , 'CreateFolder'
                          , 'FileUpload'
                           ):
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



    ##
    # Command support
    ##

    def GetFolders(self, *arg, **kw):
        """Get the list of the children folders of a folder."""
        pass

    def GetFolders_response(self, Type, CurrentFolder, ComputedUrl, folders,
                            **other):
        """Given three strings and a list, return an XML response.
        """

        folder_template = '''<Folder name="%s" />'''
        folders_xml = '\n      '.join([folder_template % f for f in folders])

        return Templates.GetFolders % ( Type
                                      , CurrentFolder
                                      , ComputedUrl
                                      , folders_xml
                                       )



    def GetFoldersAndFiles(self, *arg, **kw):
        """Gets the list of the children folders and files of a folder."""
        pass

    def GetFoldersAndFiles_response(self, Type, CurrentFolder, ComputedUrl,
                                    folders, files, **other):
        """Given three strings and two lists, return an XML response.
        """

        # folders just needs to be a list of names
        folder_template = '''<Folder name="%s" />'''
        folders_xml = '\n      '.join([folder_template % f for f in folders])

        # files needs to be a list of (name, size) tuples; size is kB
        file_template = '''<File name="%s" size="%s" />'''
        files_xml   = '\n      '.join([file_template % f for f in files])

        return Templates.GetFoldersAndFiles % ( Type
                                              , CurrentFolder
                                              , ComputedUrl
                                              , folders_xml
                                              , files_xml
                                               )



    def CreateFolder(self, *arg, **kw):
        """Create a child folder."""
        pass

    def CreateFolder_response(self, Type, CurrentFolder, ComputedUrl,
                              error_code, **other):
        """Given four strings, return an XML response.
        """

        return Templates.CreateFolder % ( Type
                                        , CurrentFolder
                                        , ComputedUrl
                                        , error_code
                                         )



    def FileUpload(self, *arg, **kw):
        """Add a file in a folder."""
        pass

    def FileUpload_response(self, param_string, **other):
        """Given a string, return an HTML response.
        """
        return Templates.FileUpload % param_string

    def _incrementFileName(self, NewFileName, filenames):
        """Given a filename and a list of filenames, return a filename variant.

        The FCK spec calls for automatically resolving filename conflicts by
        incrementing filenames like so:

          FileName.ext
          FileName(1).ext
          FileName(2).ext

        We've factored out the renaming logic since it is framework independent.
        This method takes a proposed filename and a list of existing filenames,
        and returns a properly incremented variant of NewFileName. It assumes
        that NewFileName is in filenames.

        """

        # Resolve the incoming filename into parts.
        # =========================================
        #  'File.Name.ext' -> 'File.Name', 'ext'
        #  'FileName.ext' -> 'FileName', 'ext'
        #  'FileName' -> 'FileName', ''

        parts = NewFileName.split('.')
        l = len(parts)
        if l > 1:
            name = '.'.join(parts[:-1])
            ext = parts[-1]
        elif l == 1:
            name = parts[0]
            ext = ''
        else: # l < 1
            raise FCKexception, "Bad filename: %s" % NewFileName


        # Find the next available int in the list of filenames.
        # =====================================================

        if ext:
            pattern = "%s\((\d+)\)\.%s$" % (name,ext)
        else:
            pattern = "%s\((\d+)\)$" % name
        match = re.compile(pattern).match

        ints = []
        for filename in filenames:
            candidate = match(filename)
            if candidate is not None:
                ints.append(int(candidate.group(1)))
        if ints:
            ints.sort()
            next_int = ints[-1] + 1
        else:
            next_int = 1
        next_int = str(next_int)


        # Build and return our new filename.
        # ==================================

        if ext:
            FinalFileName = '%s(%s).%s' % (name, next_int, ext)
        else:
            FinalFileName = '%s(%s)' % (name, next_int)

        return FinalFileName
