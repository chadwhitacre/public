"""Customizable Simplates that come from the filesystem.
"""

from string import split, replace
from os import stat
import re, sys

import Globals, Acquisition
from DateTime import DateTime
from DocumentTemplate.DT_Util import html_quote
from Acquisition import aq_parent
from AccessControl import getSecurityManager, ClassSecurityInfo
from Shared.DC.Scripts.Script import Script
from Products.Simplates.Simplate import Simplate
from Products.Simplates.ZopeSimplate import ZopeSimplate, Src

from Products.CMFCore.DirectoryView import registerFileExtension, registerMetaType, expandpath
from Products.CMFCore.CMFCorePermissions import ViewManagementScreens
from Products.CMFCore.CMFCorePermissions import View
from Products.CMFCore.CMFCorePermissions import FTPAccess
from Products.CMFCore.FSObject import FSObject
from Products.CMFCore.utils import _setCacheHeaders

#xml_detect_re = re.compile('^\s*<\?xml\s+')

from OFS.Cache import Cacheable

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

_marker = []  # Create a new marker object.

class FSSimplate(FSObject, Script, Simplate):
    "Wrapper for Simplate"
     
    meta_type = 'Filesystem Simplate'

    _owner = None  # Unowned

    manage_options=(
        (
            {'label':'Customize', 'action':'manage_main'},
            {'label':'Test', 'action':'ZScriptHTML_tryForm'},
            )
            +Cacheable.manage_options
        ) 

    security = ClassSecurityInfo()
    security.declareObjectProtected(View)

    security.declareProtected(ViewManagementScreens, 'manage_main')
    manage_main = PageTemplateFile('www/simplateFS.pt', globals())

    # Declare security for unprotected Simplate methods.
    security.declarePrivate('simplate_edit', 'write')

    def __init__(self, id, filepath, fullname=None, properties=None):
        FSObject.__init__(self, id, filepath, fullname, properties)
        self.ZBindings_edit(self._default_bindings)

    def _createZODBClone(self):
        """Create a ZODB (editable) equivalent of this object."""
        obj = ZopeSimplate(self.getId(), self._text, self.content_type)
        obj.expand = 0
        obj.write(self.read())
        return obj

#    def ZCacheable_isCachingEnabled(self):
#        return 0

    def _readFile(self, reparse):
        fp = expandpath(self._filepath)
        file = open(fp, 'r')    # not 'rb', as this is a text file!
        try: 
            data = file.read()
        finally: 
            file.close()
        if reparse:
#            if xml_detect_re.match(data):
#                # Smells like xml
#                self.content_type = 'text/xml'
#            else:
            try:
                del self.content_type
            except (AttributeError, KeyError):
                pass
            self.write(data)

    security.declarePrivate('read')
    def read(self):
        # Tie in on an opportunity to auto-update
        self._updateFromFS()
        return FSSimplate.inheritedAttribute('read')(self)

    ### The following is mainly taken from ZopeSimplate.py ###

    expand = 0

    func_defaults = None
    func_code = ZopeSimplate.func_code
    _default_bindings = ZopeSimplate._default_bindings

    security.declareProtected(View, '__call__')

#    def simplate_macros(self):
#        # Tie in on an opportunity to auto-reload
#        self._updateFromFS()
#        return FSSimplate.inheritedAttribute('simplate_macros')(self)

    def simplate_render(self, source=0, extra_context={}):
        self._updateFromFS()  # Make sure the template has been loaded.
        try:
            result = FSSimplate.inheritedAttribute('simplate_render')(
                                    self, source, extra_context
                                    )
            if not source:
                _setCacheHeaders(self, extra_context)
            return result

        except RuntimeError:
            if Globals.DevelopmentMode:
                err = FSSimplate.inheritedAttribute( 'simplate_errors' )( self )
                if not err:
                    err = sys.exc_info()
                err_type = err[0]
                err_msg = '<pre>%s</pre>' % replace( str(err[1]), "\'", "'" )
                msg = 'FS Simplate %s has errors: %s.<br>%s' % (
                    self.id, err_type, html_quote(err_msg) )
                raise RuntimeError, msg
            else:
                raise
                
    security.declarePrivate( '_SMPT_exec' )
    _SMPT_exec = ZopeSimplate._exec

    security.declarePrivate( '_exec' )
    def _exec(self, bound_names, args, kw):
        """Call a FSSimplate"""
        try:
            response = self.REQUEST.RESPONSE
        except AttributeError:
            response = None
        # Read file first to get a correct content_type default value.
        self._updateFromFS()
        
        if not kw.has_key('args'):
            kw['args'] = args
        bound_names['options'] = kw

        try:
            response = self.REQUEST.RESPONSE
            if not response.headers.has_key('content-type'):
                response.setHeader('content-type', self.content_type)
        except AttributeError:
            pass
            
        security=getSecurityManager()
        bound_names['user'] = security.getUser()

        # Retrieve the value from the cache.
        keyset = None
        if self.ZCacheable_isCachingEnabled():
            # Prepare a cache key.
            keyset = {
                      # Why oh why?
                      # All this code is cut and paste
                      # here to make sure that we 
                      # dont call _getContext and hence can't cache
                      # Annoying huh?
                      'here': self.aq_parent.getPhysicalPath(),
                      'bound_names': bound_names}
            result = self.ZCacheable_get(keywords=keyset)
            if result is not None:
                # Got a cached value.
                return result

        # Execute the template in a new security context.
        security.addContext(self)
        try:
            result = self.simplate_render(extra_context=bound_names)
            if keyset is not None:
                # Store the result in the cache.
                self.ZCacheable_set(result, keywords=keyset)
            return result
        finally:
            security.removeContext(self)
        
        return result
 
    # Copy over more methods
    security.declareProtected(FTPAccess, 'manage_FTPget')
    manage_FTPget = ZopeSimplate.manage_FTPget

    security.declareProtected(View, 'get_size')
    get_size = ZopeSimplate.get_size
    getSize = get_size

    security.declareProtected(ViewManagementScreens, 'PrincipiaSearchSource')
    PrincipiaSearchSource = ZopeSimplate.PrincipiaSearchSource

    security.declareProtected(ViewManagementScreens, 'document_src')
    document_src = ZopeSimplate.document_src

    simplate_getContext = ZopeSimplate.simplate_getContext

    ZScriptHTML_tryParams = ZopeSimplate.ZScriptHTML_tryParams


#s = Src()
#setattr(FSSimplate, 'source.xml', s)
#setattr(FSSimplate, 'source.html', s)
#del s

Globals.InitializeClass(FSSimplate)

registerFileExtension('smpt', FSSimplate)
registerFileExtension('smpl', FSSimplate)
registerFileExtension('spt', FSSimplate)
registerMetaType('Simplate', FSSimplate)

