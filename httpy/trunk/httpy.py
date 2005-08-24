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
import os
import re
import stat
import sys
from mimetypes import guess_type
from urllib import unquote
from urlparse import urlsplit



# Import from non-standard libraries.
# ===================================

from medusa import http_date
from medusa import http_server
from medusa import logger
from medusa import producers
from simpletal import simpleTAL
from simpletal import simpleTALES
from simpletal import simpleTALUtils


# Patch http_request to use raise.
# ================================

def _error (self, code_):
    raise RequestProblem(code_)
http_server.http_request.error = _error


# Define a problem class.
# =======================

class RequestProblem(Exception):
    """A problem with a request.
    """
    def __init__(self, code_, **kw):
        self.code = code_

        # Store any problem-specific values.
        for key, val in kw.items():
            setattr(self, key, val)

    def __str__(self):
        short_msg = http_server.http_request.responses.get(self.code)
        return '%s %s' % (str(self.code), short_msg)


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

        self.root = root
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

            # Validate the command and add `path' to the request.
            # ===================================================

            if request.command not in self.valid_commands:
                raise RequestProblem(400) # Bad Request (should be 405?)

            self.setpath(request) # This can raise 301, 400, 403, or 404.


            # Serve the resource.
            # ===================

            ext = None
            if '.' in request.path:
                ext = request.path.split('.')[-1]

            if ext not in self.extensions:
                getcontent = self.getstatic
            else:
                getcontent = self.gettemplate
            content = getcontent(request) # This can raise anything since it
                                          # provides site-specific hooks

        except RequestProblem, problem:

            content = self.getproblem(request, problem)


        if content and (request.command == 'GET'):
            request.push(self.producer(content))

        request.done()




    def getstatic(self, request):
        """Given a request for a static resource, set headers & return content.
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
                        length = int(length)
                        if length != content_length:
                            length_match = False
                    except:
                        pass

            ims_date = False
            if ims:
                ims_date = http_date.parse_http_date(ims.group(1))

            if length_match and ims_date:
                if mtime <= ims_date:
                    raise RequestProblem(304)


        # Set headers and return content.
        # ===============================

        content = open(request.path, 'rb').read()

        request['Last-Modified'] = http_date.build_http_date(mtime)
        request['Content-Length'] = content_length
        request['Content-Type'] = guess_type(request.path)[0] or 'text/plain'

        return content


    def gettemplate(self, request):
        """Given a request for a page template, set headers and return content.
        """

        # Build the context.
        # ==================

        context = simpleTALES.Context()
        context.addGlobal("frame", self.getframe())
        _path = os.path.join(self.__, 'context.py')
        if os.path.isfile(_path):
            execfile(_path, { 'request':request
                            , 'context':context
                             })


        # Expand the template.
        # ====================

        out = simpleTALUtils.FastStringOutput()
        template = self.templates.getXMLTemplate(request.path)
        template.expand( context
                       , out
                       , docType = '' # It appears that this argument is
                                      # ignored when PyXML is installed.
                       , suppressXMLDeclaration = True
                        )


        # Set headers and return the content.
        # ===================================

        content = out.getvalue()

        request['Content-Length'] = long(len(content))
        request['Content-Type'] = 'text/html'

        return content


    def getproblem(self, request, problem):
        """Given a request and an problem, set headers and return content.
        """

        # Do problem-specific processing.
        # ===============================

        if problem.code == 301: # Moved Permanently
            request['Location'] = problem.new_location
        if problem.code == 302: # Moved Permanently
            request['Location'] = problem.new_location
        elif problem.code == 304: # Not Modified
            pass

        request.reply_code == problem.code


        # Generate a problem page if we need to.
        # ======================================

        if (request.method == 'HEAD') or (problem.code == 304):

            content = ''

        else:

            template = self.getproblemtemplate()
            context = simpleTALES.Context()
            context.addGlobal("request", request)
            context.addGlobal("problem", problem)
            out = simpleTALUtils.FastStringOutput()
            template.expand( context
                           , out
                           , docType = '' # It appears that this argument is
                                          # ignored when PyXML is installed.
                           , suppressXMLDeclaration = True
                            )
            content = out.getvalue()

            request['Content-Length'] = long(len(content))
            request['Content-Type'] = 'text/html'

        return content


    def getframe(self):
        """Wrap the call to getXMLTemplate to avoid a 'not found' error.
        """
        frame_path = os.path.join(self.__, 'frame.pt')
        if os.path.exists(frame_path):
            template = self.templates.getXMLTemplate(frame_path)
            return template.macros.get('frame', None)


    def getproblemtemplate(self):
        """Wrap the call to getXMLTemplate to avoid a 'not found' error.
        """
        frame_path = os.path.join(self.__, 'problem.pt')
        if os.path.exists(frame_path):
            return self.templates.getXMLTemplate(frame_path)


    def setpath(self, request):
        """Given a request, translate the URI and store it on `path'.
        """

        # Parse the URI.
        # ==============
        # Afaict this only ever contains path and query.

        scheme, name, urlpath, query, fragment = urlsplit(request.uri)


        # Tidy up the path.
        # =================

        if not urlpath:
            # this catches, e.g., '//foo'
            raise RequestProblem(400)
        path = urlpath
        if '%' in path:
            path = unquote(path)
        path = os.path.join(self.root, path.lstrip('/'))
        path = os.path.realpath(path)
        if not path.startswith(self.root):
            # protect against '../../../../../../../../../../etc/master.passwd'
            raise RequestProblem(400)
        if self.__ and path.startswith(self.__):
            # disallow access to our magic directory
            raise RequestProblem(404)


        # Determine if the requested directory or file can be served.
        # =============================================================
        # If the path points to a directory, look for a default object.
        # If it points to a file, see if the file exists.

        if os.path.isdir(path):
            if not request.uri.endswith('/'):
                # redirect directory requests to trailing slash
                new_location = '%s/' % request.uri
                raise RequestProblem( 301 # Moved Permanently
                                    , new_location=new_location
                                     )
            found = False
            for name in self.defaults:
                _path = os.path.join(path, name)
                if os.path.isfile(_path):
                    found = True
                    path = _path
                    break
            if not found:
                raise RequestProblem(403) # Forbidden
        else:
            if not os.path.exists(path):
                raise RequestProblem(404) # Not Found


        # We made it!
        # ===========

        request.path = path



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
    handler['root'] = os.path.realpath('./root')
    handler['defaults'] = 'index.html index.pt'
    handler['extensions'] = 'pt'
    handler['mode'] = 'development'

    if not path:
        server['port'] = int(server['port'])
        handler['defaults'] = tuple(handler['defaults'].split())
        handler['extensions'] = tuple(handler['extensions'].split())
        if not os.path.isdir(handler['root']):
            raise Usage("Configuration error: site root is not a directory:" +
                        handler['root'])
        return (server, handler)

    config = ConfigParser.RawConfigParser()
    config.read(path)


    # Parse the server section.
    # =========================

    if config.has_section('server'):
        server.update(dict(config.items('server')))

    if isinstance(server['port'], basestring) and \
       server['port'].isdigit():
        server['port'] = int(server['port'])
    elif isinstance(server['port'], int):
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
        raise Usage("Configuration error: mode must be one of `development' " +
                    "and `deployment'.")
    if not os.path.isdir(handler['root']):
        raise Usage("Configuration error: site root is not a directory:" +
                    handler['root'])

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
                    raise Usage("Configuration error: %s does not " +
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
