#!/usr/bin/env python
"""httpy is an uncomplicated Python webserver. `man 1 httpy' for details.
"""

# Declare some metadata.
# ======================

__version__ = (0,1)



# Import from the standard library.
# =================================

import asyncore
import getopt
import imp
import mimetypes
import os
import re
import stat
import string
import sys
import types
import urlparse
import urllib
from StringIO import StringIO
import ConfigParser



# Import from non-standard libraries.
# ===================================

from medusa import producers
from medusa import http_server
from medusa import http_date
from medusa import logger
from simpletal import simpleTAL, simpleTALES, simpleTALUtils



# A development hook
# ==================

if 0: # turn this on to disable caching for profile testing
    def getXMLTemplateNoCache(self, name):
    	""" Name should be the path of an XML template file.
    	"""
    	#<snip>cache checking</snip>
    	return self._cacheTemplate_(name, None, xmlTemplate=1)
    simpleTALUtils.TemplateCache.getXMLTemplate = getXMLTemplateNoCache



# Define our request handler.
# ===========================

        # Clean up incoming paths and save values.
        # ========================================

        self.root = os.path.realpath(root)
        self.defaults = defaults
#        _app_paths = ()
#        for p in app_paths:
#            p = p.lstrip('/')
#            p = os.path.join(self.root, p)
#            p = os.path.realpath(p)
#            _app_paths += (p,)
#        self.app_paths = _app_paths
        self.dev_mode = os.environ.get('HTTPY_MODE','').lower() == 'development'



        # Set up a template cache.
        # ========================

        self.templates = simpleTALUtils.TemplateCache()



#        # Pre-load any applications.
#        # ==========================
#
#        apps = {}
#        for p in self.app_paths:
#            try:
#                app = self._import_app(p)
#            except ImportError:
#                raise Exception, "No module 'app.py' in %s" % p
#            else:
#                apps[p] = app(p)
#        self.apps = apps


        self.DOC_TYPE = '' # yes we make this global to the server






        # Actually serve the content.
        # ===========================

        # pages
        if path.endswith('.pt'):

            template = self.templates.getXMLTemplate(path)
            content = self._render_pt(request, template)

            #request['Last-Modified'] = http_date.build_http_date(mtime)
            #request['Content-Length'] = len(content)
            request['Content-Type'] = 'text/html'

            if request.command == 'GET':
                request.push(self.producer(content))

            request.done()
            return

        # static content
        else:

            content = file(path, 'rb').read()

            request['Last-Modified'] = http_date.build_http_date(mtime)
            request['Content-Length'] = content_length
            self.set_content_type(path, request)

            if request.command == 'GET':
                request.push(self.producer(content))

            request.done()
            return


    def set_content_type (self, path, request):
        ext = string.lower(get_extension(path))
        typ, encoding = mimetypes.guess_type(path)
        if typ is not None:
            request['Content-Type'] = typ
        else:
            request['Content-Type'] = 'text/plain'


    def frame(self):
        """Wrap the call to getXMLTemplate to avoid a 'not found' error.
        """
        frame_path = os.path.join(self.__, 'frame.pt')
        if os.path.exists(frame_path):
            return self.templates.getXMLTemplate(frame_path)


    def _render_pt(self, request, template):
        """Render a page template.

        We pass in request so that we can put it in state.py's namespace.

        """

        # Start building context and hand off to local hook.
        # ==================================================

        context = simpleTALES.Context()
        context.addGlobal("frame", self.frame())

        state_path = os.path.join(self.__, 'state.py')
        if os.path.isfile(state_path):
            execfile(state_path, { 'request':request
                                 , 'context':context
                                  })


        # Expand and return the template.
        # ===============================

        out = simpleTALUtils.FastStringOutput()
        template.expand( context
                       , out
                       , docType = self.DOC_TYPE # this doesn't appear to work with PyXML
                       , suppressXMLDeclaration = True
                        )
        return out.getvalue()


#    def _import_app(self, app_path):
#        """Manual import lifted from the docs.
#        """
#
#        NAME = 'app'
#
#        # Fast path: see if the module has already been imported.
#        try:
#            return sys.modules[NAME]
#        except KeyError:
#            pass
#
#        fp, pathname, description = imp.find_module(NAME, [app_path])
#
#        try:
#            app = imp.load_module(NAME, fp, pathname, description)
#        finally:
#            # Since we may exit via an exception, close fp explicitly.
#            if fp:
#                fp.close()
#
#        if not hasattr(app, 'Application'):
#            raise Exception, "No 'Application' class in %s/app.py" % app_path
#
#        return app.Application
