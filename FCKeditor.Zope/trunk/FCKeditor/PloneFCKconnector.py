# Python
import re
from StringIO import StringIO
from traceback import print_exc

# Zope
from AccessControl import ClassSecurityInfo, Unauthorized
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.utils import UniqueObject
from ZODB.POSException import ConflictError
from zLOG import LOG, WARNING

# us
from Products.FCKeditor.FCKconnector import FCKconnector

# constants
LIST = 'List folder contents'
VIEW = 'View'
ID = 'portal_fckconnector'


class PloneFCKconnector(FCKconnector, UniqueObject, PropertyManager,
                        SimpleItem):
    """A Plone wrapper for FCKconnector.
    """

    security = ClassSecurityInfo()

    id = ID
    title = ''
    meta_type = 'FCKconnector for Plone'

    manage_options = PropertyManager.manage_options +\
                     SimpleItem.manage_options

    def __init__(self, id, title=''):
        self.id = id
        self.title = title

    security.declarePublic('connector')
    def connector(self, REQUEST):

        """REQUEST acts like a dict, so we could hand it directly to our
        superclass. However, we need to set response headers based on Command,
        so we end up overriding. We also stick the user in there so we can
        perform security checks against it in the Get* methods.

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
        data.update(logic_method(**data)) # this adds a new key or two

        #from pprint import pprint
        #pprint(data)
        #print

        response_method = getattr(self, '%s_response' % Command)
        return response_method(**data)

    def _compute_url(self, ServerPath, Type, CurrentFolder, **other):

        """We depart from the FCK spec at this point because we don't want
        to organize our content in ResourceType folders.

        """
        return CurrentFolder

    __call__ = index_html = connector


    ##
    # Command support
    ##

    security.declarePrivate('GetFolders')
    def GetFolders(self, Type, CurrentFolder, User, **other):
        """Get the list of the children folders of a folder."""

        try:
            folder = self.unrestrictedTraverse('..'+CurrentFolder)
            exists = True
        except ConflictError: # Always raise.
            raise
        except KeyError: # The CurrentFolder doesn't exist.
            exists = False
            folders = []

        if exists:
            if not User.has_permission(LIST, folder):
                folders = []
            else:
                folders = folder.objectValues('Plone Folder')
                folders = [o.getId() for o in folders
                                           if User.has_permission(LIST, o)]

        return { 'folders' : folders }



    security.declarePrivate('GetFoldersAndFiles')
    def GetFoldersAndFiles(self, Type, CurrentFolder, User, **other):
        """Gets the list of the children folders and files of a folder."""

        try:
            folder = self.unrestrictedTraverse('..'+CurrentFolder)
            exists = True
        except ConflictError: # Always raise.
            raise
        except KeyError: # The CurrentFolder doesn't exist.
            exists = False
            folders = files = []
        if exists:
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
    def _file_info(self, o):
        """Given an object, return a tuple."""

        id = o.getId()
        size = o.get_size()
        size = float(size) / 1024 # convert to KB
        size = int(round(size))   # round to nearest KB

        return (id, size)



    security.declarePrivate('CreateFolder')
    def CreateFolder(self, Type, CurrentFolder, NewFolderName, **other):
        """Create a child folder.

        Error codes are as follows:

            0   No Errors Found. The folder has been created.
            101 Folder already exists.
            102 Invalid folder name.
            103 You have no permissions to create the folder.
            110 Unknown error creating folder.

        """

        error_code = 0

        try:
            folder = self.unrestrictedTraverse('..'+CurrentFolder)
        except ConflictError: # Always raise.
            raise
        except KeyError: # The CurrentFolder doesn't exist.
            error_code = 110

        if error_code == 0:
            if NewFolderName in folder.contentIds():
                error_code = 101
            elif folder.check_id(NewFolderName) is not None:
                error_code = 102
            else:
                try:
                    # use invokeFactory so that we trigger security
                    folder.invokeFactory('Folder', NewFolderName)
                    error_code = 0
                except ConflictError: # Always raise.
                    raise
                except Unauthorized:
                    error_code = 103
                except: # catch-all
                    error_code = 110
                    cap = StringIO()
                    print >> cap, "While trying to create a new folder via " +\
                                  "the filebrowser, the following " +\
                                  "exception was captured:\n"
                    print_exc(file=cap)
                    LOG('FCKeditor', WARNING, cap.read())
                    cap.close()

        return { 'error_code' : error_code }



    def FileUpload(self, Type, CurrentFolder, NewFile, **kw):
        """Add a file in a folder.

        Our return value gets incorporated into an HTML snippet as the paramater
        list of an ecmascript function call. The ecmascript function in question
        takes one or two parameters. The simplest thing for us to do is to
        return the parameter list as a single string rather than returning each
        parameter individually.

            OnUploadCompleted(0)
                no errors found on the upload process.

            OnUploadCompleted(201, 'FileName(1).ext')
                the file has been uploaded successfully, but its name has been
                changed to "FileName(1).ext".

            OnUploadCompleted(202)
                invalid file.

        """

        error_code = 0

        try:
            folder = self.unrestrictedTraverse('..'+CurrentFolder)
        except ConflictError: # Always raise.
            raise
        except KeyError: # The CurrentFolder doesn't exist.
            error_code = 202

        if error_code == 0:

            NewFileName = NewFile.filename

            if NewFileName not in folder.contentIds():
                FinalFileName = NewFileName
            else:
                # The FCK spec calls for automatically resolving filename
                # conflicts by incrementing filenames like so:
                #
                #   FileName.ext
                #   FileName(1).ext
                #   FileName(2).ext

                error_code = 201

                # Resolve the incoming filename into parts
                #
                #  'File.Name.ext' -> 'File.Name', 'ext'
                #  'FileName.ext' -> 'FileName', 'ext'
                #  'FileName' -> 'FileName', ''

                parts = NewFileName.split('.')
                l = len(parts) # guaranteed to be >= 1
                if l > 1:
                    name = '.'.join(parts[:-1])
                    ext = parts[-1]
                else:
                    name = parts[0]
                    ext = ''

                #
                # Find the next available int in the current folder.
                #
                if ext:
                    pattern = "%s\((\d+)\)\.%s$" % (name,ext)
                else:
                    pattern = "%s\((\d+)\)$" % name
                match = re.compile(pattern).match

                ints = []
                for id in folder.objectIds():
                    candidate = match(id)
                    if candidate is not None:
                        ints.append(int(candidate.group(1)))
                if ints:
                    ints.sort()
                    next_int = ints[-1] + 1
                else:
                    next_int = 1
                next_int = str(next_int)

                #
                # Build our new filename.
                #
                if ext:
                    FinalFileName = '%s(%s).%s' % (name, next_int, ext)
                else:
                    FinalFileName = '%s(%s)' % (name, next_int)

            try:
                # Use invokeFactory so that we trigger security.
                folder.invokeFactory('File', FinalFileName, file=NewFile)
                if error_code <> 201:
                    error_code = 0
            except ConflictError: # Always raise.
                raise
            except:
                error_code = 202
                cap = StringIO()
                print >> cap, "While trying to upload a new file via " +\
                              "the filebrowser, the following " +\
                              "exception was captured:\n"
                print_exc(file=cap)
                #print_exc() # debugging during testing -- where does ZTC
                            # log to?
                LOG('FCKeditor', WARNING, cap.read())
                cap.close()

        if error_code == 201:
            param_string = "%s, '%s'" % (str(error_code), FinalFileName)
        else:
            param_string = str(error_code)

        return { 'param_string' : str(param_string) }

InitializeClass(PloneFCKconnector)



##
# Product addition and registration
##

def manage_addPloneFCKconnector(self, REQUEST=None):
    """  """
    self._setObject(ID, PloneFCKconnector(ID))
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

def initialize(registrar):
    registrar.registerClass(
        PloneFCKconnector,
        permission='Add FCKconnector for Plone',
        constructors=(manage_addPloneFCKconnector,),
        icon='www/PloneFCKconnector.gif',
        )
