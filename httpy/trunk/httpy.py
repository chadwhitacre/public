#!/usr/bin/env python
"""httpy is an uncomplicated Python webserver. `man 1 httpy' for details.
"""

# Declare some metadata.
# ======================

__version__ = (0,1)



# Import from the standard library.
# =================================

import ConfigParser
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



# Import from non-standard libraries.
# ===================================

from medusa import http_date
from medusa import http_server
from medusa import logger
from medusa import producers
from simpletal import simpleTAL
from simpletal import simpleTALES
from simpletal import simpleTALUtils



class RequestError(Exception):
    """An error with a request.
    """
    def __init__(self, code):
        self.code = code
    def __str__(self):
        msg = http_server.http_request.responses.get(self.code)
        return '%s %s' % (str(self.code), msg)


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
    producer = producers.simple_producer

    def __init__(self, root, defaults, extensions, mode): #, app_paths=()):

        # Clean up incoming paths and save values.
        # ========================================

        self.root = os.path.realpath(root)
        self.defaults = defaults
        self.extensions = extensions
        if mode:
            self.mode = mode
        else:
            self.mode = os.environ.get('HTTPY_MODE','').lower()
        self.dev_mode = self.mode == 'development'


        # Look for a __ directory in the publishing root.
        # ===============================================

        __ = os.path.join(self.root, '__')
        if os.path.isdir(__):
            self.__ = __
            sys.path.insert(0, __)
        else:
            self.__ = ''


        # Set up a template cache.
        # ========================

        self.templates = simpleTALUtils.TemplateCache()


    def handle_request(self, request):
        """Handle an HTTP request.
        """

        try:

            # Command
            # =======

            if request.command not in self.valid_commands:
                raise RequestError(400) # bad request


            # Add path info to request.
            # =========================
            self.path_info(request)


            # Serve content.
            # ==============

            if '.' in request.path:
                if request.path.split('.')[-1] in self.extensions:
                    self.handle_template(request)
            else:
                self.handle_static(request)

        except RequestError, err:
            request.error(err.code)
            return


    def path_info(self, request):
        """Given a request, add two attributes.

        The requested path is stored in `urlpath', and the resolved path in
        `path'.

        """

        # Parse the URI.
        # ==============
        # Afaict this only ever contains path and query.

        scheme, name, urlpath, query, fragment = urlparse.urlsplit(request.uri)


        # Tidy up the path.
        # =================

        if not urlpath:
            # this catches, e.g., '//foo'
            raise RequestError(400)
        path = urlpath
        if '%' in path:
            path = urllib.unquote(path)
        path = os.path.join(self.root, path.lstrip('/'))
        path = os.path.realpath(path)
        if not path.startswith(self.root):
            # protect against '../../../../../../../../../../etc/master.passwd'
            raise RequestError(400)


        # Determine if the requested directory or file can be served.
        # =============================================================
        # If the path points to a directory, look for a default object.
        # If it points to a file, see if the file exists.

        if os.path.isdir(path):
            found = False
            for name in self.defaults:
                _path = os.path.join(path, name)
                if os.path.isfile(_path):
                    found = True
                    path = _path
                    break
            if not found:
                raise RequestError(403) # Forbidden
        else:
            if not os.path.exists(path):
                raise RequestError(404) # Not Found


        # We made it! Set the variables on request.
        # =========================================

        request.path = path
        request.urlpath = urlpath



    def handle_template(self, request):
        """Given a request for a page template, serve it.
        """

        # Build the context.
        # ==================

        context = simpleTALES.Context()
        context.addGlobal("frame", self.frame())
        _path = os.path.join(self.__, 'context.py')
        if os.path.isfile(_path):
            execfile(_path, { 'request':request
                            , 'context':context
                             })


        # Expand and return the template.
        # ===============================

        out = simpleTALUtils.FastStringOutput()
        template = self.templates.getXMLTemplate(request.path)
        template.expand( context
                       , out
                       , docType = self.DOC_TYPE # this doesn't appear to work with PyXML
                       , suppressXMLDeclaration = True
                        )


        # Set headers and return.
        # =======================

        request['Content-Type'] = 'text/html'

        if request.command == 'GET':
            request.push(self.producer(out.getvalue()))

        request.done()
        return


    def handle_static(self, request):
        """Given a request for a static resource, serve it.
        """

        # Serve a 304 if appropriate.
        # ===========================

        mtime = os.stat(request.path)[stat.ST_MTIME]
        content_length = os.stat(request.path)[stat.ST_SIZE]

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


        # Serve the resource.
        # ===================

        content = file(request.path, 'rb').read()

        request['Last-Modified'] = http_date.build_http_date(mtime)
        request['Content-Length'] = content_length
        self.set_content_type(request.path, request)

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



# Request parsers from medusa.default_handler
# ===========================================

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



# main() a la Guido
# =================
# http://www.artima.com/weblogs/viewpost.jsp?thread=4829

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def parse_config(path):
    """Given a path to a configuration file, return two dictionaries.
    """

    # Set defaults.
    # =============

    server = {}
    server['ip'] = ''
    server['port'] = '8080'

    handler = {}
    handler['root'] = './root'
    handler['defaults'] = 'index.html index.pt'
    handler['extensions'] = 'pt'
    handler['mode'] = 'development'


    if not path:
        server['port'] = int(server['port'])
        handler['defaults'] = tuple(handler['defaults'].split())
        handler['extensions'] = tuple(handler['extensions'].split())
        return (server, handler)

    config = ConfigParser.RawConfigParser()
    config.read(path)


    # Parse the server section.
    # =========================

    if config.has_section('server'):
        server.update(dict(config.items('server')))

    if isinstance(server['port'], types.StringType) and \
       server['port'].isdigit():
        server['port'] = int(server['port'])
    elif isinstance(server['port'], types.IntType):
        pass # already an int for some reason (called interactively?)
    else:
        raise Usage("Configuration error: port must be an integer")


    # Parse the handler section.
    # ==========================

    if config.has_section('handler'):
        handler.update(dict(config.items('handler')))

    handler['defaults'] = tuple(handler['defaults'].split())
    handler['extensions'] = tuple(handler['extensions'].split())
    if handler['mode'].lower() not in ('development', 'deployment'):
        raise Usage("Configuration error: mode must be one of `development' " +\
                    "and `deployment'.")

    return (server, handler)


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:

        # Identify our configuration file.
        # ================================

        if argv[1:]:
            try:
                opts, args = getopt.getopt(argv[1:], "f:")
                opts = dict(opts)
                path = os.path.realpath(opts.get('-f'))
                if not os.path.isfile(path):
                    raise Usage("Configuration error: %s does not " +\
                                "exist." % path)
            except getopt.error, msg:
                raise Usage(msg)
        else:
            path = None


        # Parse our configuration file.
        # =============================

        try:
            _server, _handler = parse_config(path)
        except ConfigParser.Error, msg:
            raise Usage("Configuration error: %s" % msg)


        # Stop, drop, and roll.
        # =====================

        server = http_server.http_server(**_server)
        server.install_handler(handler(**_handler))
        asyncore.loop()


    except Usage, err:
        print >> sys.stderr, err.msg
        print >> sys.stderr, "`man 1 httpy' for usage."
        return 2


if __name__ == "__main__":
    sys.exit(main())
