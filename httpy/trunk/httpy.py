#!/usr/bin/env python
"""This is an http server for uncomplicated, Python-based websites.

httpy recognizes serves three different kinds of resources:

    - Files with names ending in .pt are interpreted as page templates and are
      compiled using SimpleTAL.

    - Files named app.py are considered to be applications and are handed the
      current request to do with as they please.

    - All other files are served as-is from the filesystem.


httpy requires one option with one required argument, -f, which specifies the
configuration file to use in starting the server. The configuration file is in
the style of Windows INI files, with two sections and five possible values. Here
is a complete sample configuration file showing the default options:

    [network]
    ip          =
    port        = 8080

    [filesystem]
    root        = ./root
    defaults    = index.html index.pt
    log         =


The names of the configuration options are case-insensitive, and the values are
case-preserved. Here are explanations of the options:

    ip -- The IP address to listen on. If left blank, httpy will listen on all
    available addresses.

    port -- The TCP port of the specified network interface to listen on.

    root -- The path to the directory to use as the root of httpy's URL-space.

    defaults -- A whitespace-separated list of filenames to default to when a
    directory is requested directly.

    log -- The path to a file to which messages should be logged.


httpy has two modes of operation: development and deployment. In development mode,


    - the publisher does three things:

        - serves page templates through simpletal, with two hooks:

            - root/__/frame.pt will be added to the context as a global macro

            - root/__/state.py will be execfile'd before compilation

        - hands off control flow to applications when called to

        - serves static files

    - should the publisher manage sessions, cookies, post, querystring?

    - the publisher should have two modes: development and deployment

        - development mode:

            - all templates are compiled on the fly (trivial)

            - all modules are reimported on the fly (non-trivial)

            - the point is that we want to change a file on the fs and hit f5 in
            the browser w/o restarting the server process

        - deployment mode:

            - all templates are compiled only at startup (non-trivial)

            - modules are not reimported (trivial)

            - pre-compiling templates is necessary for performance reasons


    - deployment should mean compiling all of our page templates to html and
    only serving the static versions. there's no good reason to do all that
    processing on every fritten request.

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

class handler:
    """This is copied, pasted, and modified from medusa.default_handler.
    """

    # I assume these are Medusa boilerplate
    IDENT = 'Default HTTP Request Handler'
    # always match, since this is a default
    def match (self, request):
        return 1

    # these at least appear in this file
    valid_commands = ['GET', 'HEAD']
    default_file_producer = producers.simple_producer

    def __init__(self, root='.', defaults=(), app_paths=(), dev_mode=False):

        # Clean up incoming paths and save values.
        # ========================================

        self.root = os.path.realpath(root)
        self.defaults = defaults
        _app_paths = ()
        for p in app_paths:
            p = p.lstrip('/')
            p = os.path.join(self.root, p)
            p = os.path.realpath(p)
            _app_paths += (p,)
        self.app_paths = _app_paths
        self.dev_mode = os.environ.get('DEV_MODE','').lower() == 'true'


        # Look for a __ directory in the publishing root.
        # ===============================================

        __ = os.path.join(self.root, '__')
        if os.path.isdir(__):
            self.__ = __
            sys.path.insert(0, __)
        else:
            self.__ = ''

        self.templates = simpleTALUtils.TemplateCache()


        # Pre-load any applications.
        # ==========================

        apps = {}
        for p in self.app_paths:
            try:
                app = self._import_app(p)
            except ImportError:
                raise Exception, "No module 'app.py' in %s" % p
            else:
                apps[p] = app(p)
        self.apps = apps


        self.DOC_TYPE = '' # yes we make this global to the server


    def handle_request(self, request):
        """Handle an HTTP request.
        """

        # Re-init for dev mode.
        # =====================

        if self.dev_mode and 0:
            self.__pre__()


        # Command
        # =======

        if request.command not in self.valid_commands:
            request.error(400) # bad request
            return


        # Path
        # ====

        # parse the uri -- only ever contains path and query(?)
        scheme, name, path, query, fragment = urlparse.urlsplit(request.uri)

        # tidy up the path
        if '%' in path:
            path = urllib.unquote(path)
        path = os.path.join(self.root, path.lstrip('/'))
        path = os.path.realpath(path)



        # Applications
        # ============
        # determine if the url belongs to one of our apps
        # if so then hand off control flow to the application

        for p in self.app_paths:
            if path.startswith(p):
                app = self.apps[p]
                app(request)
                return



        # Pages & Static Content
        # ======================

        # see if the path is valid
        if not os.path.exists(path):
            request.error(404)
            return
        elif not path.startswith(self.root):
            # protect against ./../../../
            request.error(400)
            return

        # if the path points to a directory, look for a default obj
        if os.path.isdir(path):
            # look for a default object
            found = False
            for name in self.defaults:
                _path = os.path.join(path, name)
                if os.path.isfile(_path):
                    found = True
                    path = _path
                    break
            if not found: # no default object
                request.error(404)
                return

        # save this for later use in state.py -- hack atm
        request.path = path



        # Decide if the content has changed recently.
        # ===========================================

        mtime = os.stat(path)[stat.ST_MTIME]
        content_length = os.stat(path)[stat.ST_SIZE]

        if not self.dev_mode:

            ims = get_header_match(IF_MODIFIED_SINCE, request.header)

            length_match = True
            if ims:
                length = ims.group(4)
                if length:
                    try:
                        length = string.atoi(length)
                        if length != content_length:
                            length_match = False
                    except:
                        pass

            ims_date = False
            if ims:
                ims_date = http_date.parse_http_date(ims.group(1))

            if length_match and ims_date:
                if mtime <= ims_date:
                    request.reply_code = 304
                    request.done()
                    return



        # Actually serve the content.
        # ===========================

        # pages
        if path.endswith('.pt'):

            template = self.templates.getXMLTemplate(path)
            #self.log(self.templates.hits)
            content = self._render_pt(request, template)

            #request['Last-Modified'] = http_date.build_http_date(mtime)
            #request['Content-Length'] = len(content)
            request['Content-Type'] = 'text/html'

            if request.command == 'GET':
                request.push(self.default_file_producer(content))

            request.done()
            return

        # static content
        else:

            content = file(path, 'rb').read()

            request['Last-Modified'] = http_date.build_http_date(mtime)
            request['Content-Length'] = content_length
            self.set_content_type(path, request)

            if request.command == 'GET':
                request.push(self.default_file_producer(content))

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

        We pass in request so that it is in state.py's namespace.

        """

        # Start building context and hand off to local hook.
        # ==================================================

        context = simpleTALES.Context()
        context.addGlobal("frame", self.frame())

        state_path = os.path.join(self.__, 'state.py')
        if os.path.isfile(state_path):
            execfile(state_path, locals())


        # if it is the call to expand that is taking so much time, then we could
        # try caching globals here (keyed to an MD5 of a pickle?)


        # Expand and return the template.
        # ===============================

        out = simpleTALUtils.FastStringOutput()
        template.expand( context
                       , out
                       , docType = self.DOC_TYPE # this doesn't appear to work with PyXML
                       , suppressXMLDeclaration = True
                        )
        return out.getvalue()


    def _import_app(self, app_path):
        """Manual import lifted from the docs.
        """

        NAME = 'app'

        # Fast path: see if the module has already been imported.
        try:
            return sys.modules[NAME]
        except KeyError:
            pass

        fp, pathname, description = imp.find_module(NAME, [app_path])

        try:
            app = imp.load_module(NAME, fp, pathname, description)
        finally:
            # Since we may exit via an exception, close fp explicitly.
            if fp:
                fp.close()

        if not hasattr(app, 'Application'):
            raise Exception, "No 'Application' class in %s/app.py" % app_path

        return app.Application


# Goofiness from medusa.default_handler
# =====================================

# HTTP/1.0 doesn't say anything about the "; length=nnnn" addition
# to this header.  I suppose its purpose is to avoid the overhead
# of parsing dates...
IF_MODIFIED_SINCE = re.compile (
        'If-Modified-Since: ([^;]+)((; length=([0-9]+)$)|$)',
        re.IGNORECASE
        )

USER_AGENT = re.compile ('User-Agent: (.*)', re.IGNORECASE)

CONTENT_TYPE = re.compile (
        r'Content-Type: ([^;]+)((; boundary=([A-Za-z0-9\'\(\)+_,./:=?-]+)$)|$)',
        re.IGNORECASE
        )

get_header = http_server.get_header
get_header_match = http_server.get_header_match

def get_extension (path):
    dirsep = string.rfind (path, '/')
    dotsep = string.rfind (path, '.')
    if dotsep > dirsep:
        return path[dotsep+1:]
    else:
        return ''



# main() a la Guido.
# ==================
# http://www.artima.com/weblogs/viewpost.jsp?thread=4829

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:

        # Identify our configuration file.
        # ================================

        if len(argv) < 2:
            raise Usage("Configuration error: no file specified.")
        try:
            opts, args = getopt.getopt(argv[1:], "f:")
            opts = dict(opts)
            path = os.path.realpath(opts.get('-f'))
            if not os.path.isfile(path):
                raise Usage("Configuration error: %s does not exist." % path)
        except getopt.error, msg:
            raise Usage(msg)



        # Parse our configuration file.
        # =============================

        config = ConfigParser.RawConfigParser()
        try:
            config.read(path)


            # network section

            network = {}
            network['ip'] = ''
            network['port'] = '8080'
            if config.has_section('network'):
                network.update(dict(config.items('network')))

            if isinstance(network['port'], types.StringType) and \
               network['port'].isdigit():
                network['port'] = int(network['port'])
            elif isinstance(network['port'], types.IntType):
                pass # already an int for some reason (called interactively?)
            else:
                raise Usage("Configuration error: port must be an integer")


            # filesystem section

            filesystem = {}
            filesystem['root'] = './root'
            filesystem['defaults'] = 'index.html, index.pt'
            filesystem['log'] = sys.stdout
            if config.has_section('filesystem'):
                filesystem.update(dict(config.items('filesystem')))

            filesystem['defaults'] = tuple(filesystem['defaults'].split())

            if 'log' in filesystem: # always True
                # Conceptually, this fits in filesystem, so that's where we
                # want it in the end-user config file. However, our callables
                # want it in network, and we allow that placement in the
                # config file as well.
                network['log'] = filesystem['log']
                del filesystem['log']
            if 'log' in network: # always True
                # And actually, we want to wrap this in an object.
                if not network['log']:
                    network['log'] = sys.stdout
                network['logger_object'] = logger.file_logger(network['log'])
                del network['log']

        except ConfigParser.Error, msg:
            raise Usage("Configuration error: %s" % msg)



        # Stop, drop, and roll.
        # =====================

        server = http_server.http_server(**network)
        server.install_handler(handler(**filesystem))
        asyncore.loop()


    except Usage, err:
        print >> sys.stderr, err.msg
        print >> sys.stderr, "`man 1 httpy' for usage."
        return 2

if __name__ == "__main__":
    sys.exit(main())
