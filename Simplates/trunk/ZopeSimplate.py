"""Simplate module

Zope object encapsulating a Simplate.
"""

#__version__='$Revision: 1.44.44.5 $'[11:-2]

import os, AccessControl, Acquisition, sys
from types import StringType
from Globals import DTMLFile, ImageFile, MessageDialog, package_home
from zLOG import LOG, ERROR, INFO
from OFS.SimpleItem import SimpleItem
from DateTime.DateTime import DateTime
from Shared.DC.Scripts.Script import Script, BindingsUI
from Shared.DC.Scripts.Signature import FuncCode
from AccessControl import getSecurityManager
try:
    from AccessControl import Unauthorized
except ImportError:
    Unauthorized = "Unauthorized"
from OFS.History import Historical, html_diff
from OFS.Cache import Cacheable
from OFS.Traversable import Traversable
from OFS.PropertyManager import PropertyManager
from Simplate import Simplate
#from Expressions import SecureModuleImporter
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.utils import registerIcon

try:
    from webdav.Lockable import ResourceLockedError
    from webdav.WriteLockInterface import WriteLockInterface
    SUPPORTS_WEBDAV_LOCKS = 1
except ImportError:
    SUPPORTS_WEBDAV_LOCKS = 0

class ZopeSimplate(Script, Simplate, Historical, Cacheable,
                       Traversable, PropertyManager):
    "Zope wrapper for Simplate using python string replacement"

    if SUPPORTS_WEBDAV_LOCKS:
        __implements__ = (WriteLockInterface,)

    meta_type = 'Simplate'

    func_defaults = None
    func_code = FuncCode((), 0)

    _default_bindings = {'name_subpath': 'traverse_subpath'}
    _default_content_fn = os.path.join(package_home(globals()),
                                       'www', 'default.html')

    manage_options = (
        {'label':'Edit', 'action':'simplate_editForm',
         'help': ('Simplates', 'Simplate_Edit.stx')},
        {'label':'Test', 'action':'ZScriptHTML_tryForm'},
        ) + PropertyManager.manage_options \
        + Historical.manage_options \
        + SimpleItem.manage_options \
        + Cacheable.manage_options

    _properties=({'id':'title', 'type': 'string', 'mode': 'w'},
                 {'id':'content_type', 'type':'string', 'mode': 'w'},
                 #{'id':'expand', 'type':'boolean', 'mode': 'w'},
                 {'id':'value_paths', 'type':'lines', 'mode': 'w'},
                 )

    def __init__(self, id, text='(empty)', content_type=None, value_paths=[]):
        self.id = str(id)
        self.ZBindings_edit(self._default_bindings)
        if text is None:
            text = open(self._default_content_fn).read()
        self.simplate_edit(text, content_type)
        self.simplate_setValue_paths(value_paths)

    def _setPropValue(self, id, value):
        PropertyManager._setPropValue(self, id, value)
        self.ZCacheable_invalidate()

    security = AccessControl.ClassSecurityInfo()

    security.declareObjectProtected('View')
    security.declareProtected('View', '__call__')

    security.declareProtected('View management screens',
                              'simplate_editForm',
                              'manage_main',
                              'read',
                              'ZScriptHTML_tryForm',
                              'PrincipiaSearchSource',
                              'document_src',
#                              'source.html',
#                              'source.xml',
                              )

    security.declareProtected('FTP access',
                              'manage_FTPstat',
                              'manage_FTPget',
                              'manage_FTPlist',
                              )

    simplate_editForm = PageTemplateFile('www/simplateEdit.pt', globals(),
                                   __name__='simplate_editForm')
    simplate_editForm._owner = None
    manage = manage_main = simplate_editForm

    security.declareProtected('Change simplates',
                              'simplate_editAction',
                              'simplate_setTitle',
                              'simplate_setValue_paths',
                              'simplate_edit',
                              'simplate_upload',
                              'simplate_changePrefs',
                              )
                              
                              
    def simplate_editAction(self, REQUEST, title, text, content_type, value_paths):
        """Change the title and document."""
        if SUPPORTS_WEBDAV_LOCKS and self.wl_isLocked():
            raise ResourceLockedError, "File is locked via WebDAV"
        self.simplate_setTitle(title)
        self.simplate_setValue_paths(value_paths)
        self.simplate_edit(text, content_type)
        REQUEST.set('text', self.read()) # May not equal 'text'!
        message = "Saved changes."
        if getattr(self, '_v_warnings', None):
            message = ("<strong>Warning:</strong> <i>%s</i>"
                       % '<br>'.join(self._v_warnings))
        return self.simplate_editForm(manage_tabs_message=message)

    def simplate_setTitle(self, title):
        self._setPropValue('title', str(title))

    def simplate_setValue_paths(self, value_paths):
        self._setPropValue('value_paths', list(value_paths))
        self._cook()

    def simplate_upload(self, REQUEST, file=''):
        """Replace the document with the text in file."""
        if SUPPORTS_WEBDAV_LOCKS and self.wl_isLocked():
            raise ResourceLockedError, "File is locked via WebDAV"

        if type(file) is not StringType:
            if not file: raise ValueError, 'File not specified'
            file = file.read()

        self.write(file)
        message = 'Saved changes.'
        return self.simplate_editForm(manage_tabs_message=message)

    def simplate_changePrefs(self, REQUEST, height=None, width=None,
                       dtpref_cols="100%", dtpref_rows="20"):
        """Change editing preferences."""
        dr = {"Taller":5, "Shorter":-5}.get(height, 0)
        dc = {"Wider":5, "Narrower":-5}.get(width, 0)
        if isinstance(height, int): dtpref_rows = height
        if isinstance(width, int) or \
           isinstance(width, str) and width.endswith('%'):
            dtpref_cols = width
        rows = str(max(1, int(dtpref_rows) + dr))
        cols = str(dtpref_cols)
        if cols.endswith('%'):
           cols = str(min(100, max(25, int(cols[:-1]) + dc))) + '%'
        else:
           cols = str(max(35, int(cols) + dc))
        e = (DateTime("GMT") + 365).rfc822()
        setCookie = REQUEST["RESPONSE"].setCookie
        setCookie("dtpref_rows", rows, path='/', expires=e)
        setCookie("dtpref_cols", cols, path='/', expires=e)
        REQUEST.other.update({"dtpref_cols":cols, "dtpref_rows":rows})
        return self.manage_main()

    def ZScriptHTML_tryParams(self):
        """Parameters to test the script with."""
        return []

    def manage_historyCompare(self, rev1, rev2, REQUEST,
                              historyComparisonResults=''):
        return ZopeSimplate.inheritedAttribute(
            'manage_historyCompare')(
            self, rev1, rev2, REQUEST,
            historyComparisonResults=html_diff(rev1._text, rev2._text) )

    def simplate_getContext(self):
        root = self.getPhysicalRoot()
        context = self._getContext()
        c = {'template': self,
             'here': context,
             'context': context,
             'container': self._getContainer(),
             'nothing': None,
             'options': {},
             'root': root,
             'request': getattr(root, 'REQUEST', None),
             'modules': SecureModuleImporter,
             }
        return c

    def write(self, text):
        self.ZCacheable_invalidate()
        ZopeSimplate.inheritedAttribute('write')(self, text)

    def _exec(self, bound_names, args, kw):
        """Call a simplate"""
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
            keyset = {'here': self._getContext(),
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

    security.declareProtected('Change simplates',
                              'PUT',
                              'manage_FTPput',
                              'write',
                              'manage_historyCopy',
                              'manage_beforeHistoryCopy',
                              'manage_afterHistoryCopy',
                              )

    def PUT(self, REQUEST, RESPONSE):
        """ Handle HTTP PUT requests """
        self.dav__init(REQUEST, RESPONSE)
        if SUPPORTS_WEBDAV_LOCKS:
            self.dav__simpleifhandler(REQUEST, RESPONSE, refresh=1)
        self.write(REQUEST.get('BODY', ''))
        RESPONSE.setStatus(204)
        return RESPONSE

    manage_FTPput = PUT

    def manage_FTPget(self):
        "Get source for FTP download"
        self.REQUEST.RESPONSE.setHeader('Content-Type', self.content_type)
        return self.read()

    def get_size(self):
        return len(self.read())
    getSize = get_size

    def PrincipiaSearchSource(self):
        "Support for searching - the document's contents are searched."
        return self.read()

    def document_src(self, REQUEST=None, RESPONSE=None):
        """Return expanded document source."""

        if RESPONSE is not None:
            RESPONSE.setHeader('Content-Type', 'text/plain')
        if REQUEST is not None and REQUEST.get('raw'):
            return self._text
        return self.read()

    def om_icons(self):
        """Return a list of icon URLs to be displayed by an ObjectManager"""
        icons = ({'path': 'misc_/Simplates/simplate.png',
                  'alt': self.meta_type,
                  'title': self.meta_type},)
        if not self._v_cooked:
            self._cook()
        if self._v_errors:
            icons = icons + ({'path': 'misc_/Simplates/exclamation.gif',
                              'alt': 'Error',
                              'title': 'This simplate has an error'},)
        return icons

    def __setstate__(self, state):
        # This is here for backward compatibility. :-(
        ZopeSimplate.inheritedAttribute('__setstate__')(self, state)

    def simplate_source_file(self):
        """Returns a file name to be compiled into the TAL code."""
        try:
            return '/'.join(self.getPhysicalPath())
        except:
            # This simplate is being compiled without an
            # acquisition context, so we don't know where it is. :-(
            return None

    if not SUPPORTS_WEBDAV_LOCKS:
        def wl_isLocked(self):
            return 0


class Src(Acquisition.Explicit):
    " "

    PUT = document_src = Acquisition.Acquired
    index_html = None

    def __before_publishing_traverse__(self, ob, request):
        if getattr(request, '_hacked_path', 0):
            request._hacked_path = 0

    def __call__(self, REQUEST, RESPONSE):
        " "
        return self.document_src(REQUEST)

d = ZopeSimplate.__dict__
#d['source.xml'] = d['source.html'] = Src()



##
# Product registration and Add support
##

manage_addSimplateForm = PageTemplateFile(
    'www/simplateAdd.pt', globals(), __name__='manage_addSimplateForm')

from urllib import quote

def manage_addSimplate(self, id, title=None, text=None,
                           REQUEST=None, submit=None):
    "Add a Simplate with optional file content."

    id = str(id)
    if REQUEST is None:
        self._setObject(id, ZopeSimplate(id, text))
        ob = getattr(self, id)
        if title:
            ob.simplate_setTitle(title)
        return ob
    else:
        file = REQUEST.form.get('file')
        headers = getattr(file, 'headers', None)
        if headers is None or not file.filename:
            smpt = ZopeSimplate(id, text)
        else:
            smpt = ZopeSimplate(id, file, headers.get('content_type'))

        self._setObject(id, smpt)
        if title:
            ob = getattr(self, id)
            ob.simplate_setTitle(title)

        try:
            u = self.DestinationURL()
        except AttributeError:
            u = REQUEST['URL1']

        if submit == " Add and Edit ":
            u = "%s/%s" % (u, quote(id))
        REQUEST.RESPONSE.redirect(u+'/manage_main')
    return ''

def initialize(context):
    context.registerClass(
        ZopeSimplate,
        permission='Add Simplates',
        constructors=(manage_addSimplateForm,
                      manage_addSimplate),
        icon='www/simplate.png',
        )
    context.registerHelp()
    context.registerHelpTitle('Zope Help')
    registerIcon(ZopeSimplate, 'www/exclamation.gif', globals())
