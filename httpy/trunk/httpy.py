#!/usr/bin/env python
"""httpy is an uncomplicated Python webserver. `man 1 httpy' for details.
"""

# Declare some metadata.
# ======================

__version__ = (0,1)



# Import from the standard library.
# =================================

import asyncore
import os
import re
import stat
import sys
from ConfigParser import RawConfigParser
from mimetypes import guess_type
from optparse import OptionParser
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


# Set up some error handling artifacts.
# =====================================

def _error (self, code_):
    raise RequestError(code_)
http_server.http_request.error = _error

http_server.http_request.responses[302] = 'Found'

http_server.http_request.DEFAULT_ERROR_MESSAGE = """\
<head>
    <title>Error response</title>
</head>
<body>
    <h1>Error response</h1>
    <p>Error code %d.</p>
    <p>Message: %s.</p>
    %s
</body>"""

class RequestError(Exception):
    """An error with a request.
    """
    def __init__(self, code_):
        self.code = code_
        self.msg = http_server.http_request.responses.get(code_)
        self.message = ''

class Redirect(RequestError):
    """A convenience class for triggering redirects.
    """
    def __init__(self, new_location='/', permanent=False):
        self.new_location = new_location
        code_ = permanent and 301 or 302
        RequestError.__init__(self, code_)


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

        # Initialize values.
        # ==================

        self.root = root
        self.defaults = defaults
        self.extensions = extensions
        self.mode = mode


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
                raise RequestError(400) # Bad Request (should be 405?)

            self.setpath(request) # This can raise 301, 400, 403, or 404.


            # Serve the resource.
            # ===================

            ext = None
            if '.' in request.path:
                ext = request.path.split('.')[-1]

            if ext not in self.extensions:
                getcontent = self.getstatic # This can raise 304.
            else:
                getcontent = self.gettemplate # This can raise anything since
                                              # sites have a hook.
            content = getcontent(request)

        except RequestError, error:

            content = self.geterror(request, error)


        if content and (request.command == 'GET'):
            request.push(self.producer(content))

        request.done()


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
            raise RequestError(400)
        path = urlpath
        if '%' in path:
            path = unquote(path)
        path = os.path.join(self.root, path.lstrip('/'))
        path = os.path.realpath(path)
        if not path.startswith(self.root):
            # protect against '../../../../../../../../../../etc/master.passwd'
            raise RequestError(400)
        if self.__ and path.startswith(self.__):
            # disallow access to our magic directory
            raise RequestError(404)


        # Determine if the requested directory or file can be served.
        # =============================================================
        # If the path points to a directory, look for a default object.
        # If it points to a file, see if the file exists.

        if os.path.isdir(path):
            if not request.uri.endswith('/'):
                # redirect directory requests to trailing slash
                new_location = '%s/' % request.uri
                raise Redirect( new_location
                              , permanent=True # 301
                               )
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


        # We made it!
        # ===========

        request.path = path


    def getstatic(self, request):
        """Given a request for a static resource, set headers & return content.
        """

        # Serve a 304 if appropriate.
        # ===========================

        mtime = os.stat(request.path)[stat.ST_MTIME]
        content_length = os.stat(request.path)[stat.ST_SIZE]

        if self.mode == 'deployment':

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
                    raise RequestError(304)


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
        context.addGlobal("frame", self._getframe())
        _path = os.path.join(self.__, 'context.py')
        if os.path.isfile(_path):
            execfile(_path, { 'request':request
                            , 'context':context
                            , 'Redirect':Redirect
                            , 'RequestError':RequestError
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


    def geterror(self, request, error):
        """Given a request and an error, set headers and return content.
        """

        # Do error-specific processing.
        # =============================

        if error.code in (301, 302): # Moved Permanently, Found
            request['Location'] = error.new_location
            error.message = 'Resource now resides at ' +\
                              '<a href="%s">%s</a>.' % ( error.new_location
                                                       , error.new_location
                                                        )
        elif error.code == 304: # Not Modified
            pass

        request.reply_code = error.code


        # Generate an error page if we need to.
        # =====================================

        if (request.command == 'HEAD') or (error.code == 304):

            content = ''

        else:

            template = self._geterrortemplate()

            if not template:

                errmsg = request.DEFAULT_ERROR_MESSAGE
                content = errmsg % (error.code, error.msg, error.message)

            else:

                context = simpleTALES.Context()
                context.addGlobal("request", request)
                context.addGlobal("error", error)
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


    def _getframe(self):
        """Wrap the call to getXMLTemplate to avoid a 'not found' error.
        """
        _path = os.path.join(self.__, 'frame.pt')
        if os.path.exists(_path):
            template = self.templates.getXMLTemplate(_path)
            return template.macros.get('frame', None)


    def _geterrortemplate(self):
        """Wrap the call to getXMLTemplate to avoid a 'not found' error.
        """
        _path = os.path.join(self.__, 'error.pt')
        if os.path.exists(_path):
            return self.templates.getXMLTemplate(_path)


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

class ConfigError(Exception):
    def __init__(self, msg):
        self.msg = msg


class Configuration:
    """Determine the config for an httpy server from four sources:

        - defaults -- a set of defaults
        - env -- environment variables
        - file_ -- a configuration file
        - opts -- command line options

    For each context, a dictionary is built from that context, and then
    validated: if possible, values are coerced to the requisite types; if not,
    ConfigurationError is raised. These dictionaries are combined in the order
    given above, such that environment variables override defaults, etc.
    Finally, the combined dictionary is split into two, one representing server
    configuration, and one handler configuration.

    """

    def __init__(self, argv):

        # Read them in reverse order because any file path is in opts.

        opts, path = self._opts(argv)
        file_ = self._file(path)
        env = self._env()
        defaults = self._defaults()

        # If we make it this far without an exception then we have clean data.

        total = {}
        total.update(defaults)
        total.update(env)
        total.update(file_)
        total.update(opts)

        self.server = {}
        self.server['ip'] = total['ip']
        self.server['port'] = total['port']

        self.handler = {}
        self.handler['root'] = total['root']
        self.handler['defaults'] = total['defaults']
        self.handler['extensions'] = total['extensions']
        self.handler['mode'] = total['mode']


    def _defaults(self):

        d = {}
        d['ip'] = ''
        d['port'] = 8080
        d['root'] = os.path.realpath('.')
        d['defaults'] = 'index.html index.pt'
        d['extensions'] = 'pt'
        d['mode'] = 'development'

        return self._validate('defaults', d)


    def _env(self):

        d = {}

        if os.environ.has_key('HTTPY_IP'):
            d['ip'] = os.environ.get('HTTPY_IP')
        if os.environ.has_key('HTTPY_PORT'):
            d['port'] = os.environ.get('HTTPY_PORT')
        if os.environ.has_key('HTTPY_ROOT'):
            d['root'] = os.environ.get('HTTPY_ROOT')
        if os.environ.has_key('HTTPY_DEFAULTS'):
            d['defaults'] = os.environ.get('HTTPY_DEFAULTS')
        if os.environ.has_key('HTTPY_EXTENSIONS'):
            d['extensions'] = os.environ.get('HTTPY_EXTENSIONS')
        if os.environ.has_key('HTTPY_MODE'):
            d['mode'] = os.environ.get('HTTPY_MODE')

        return self._validate('env', d)


    def _opts(self, argv):
        """Special case: return a valid dictionary *and* a config file path.
        """

        d = {}
        path = ''

        if not argv[1:]:
            return d, path

        usage = "for details, `man 1 httpy'."

        parser_ = OptionParser(usage=usage)
        parser_.add_option("-f", "--file", dest="path",
                           help="The path to a configuration file. [none]")
        parser_.add_option("-i", "--ip", dest="ip",
                           help="The IP address to listen on. [all]")
        parser_.add_option("-p", "--port", dest="port",
                           help="The TCP port to listen on. [8080]")
        parser_.add_option("-r", "--root", dest="root",
                           help="The path to the website root. [.]")
        parser_.add_option("-d", "--defaults", dest="defaults",
                           help="Attempt to serve these files when a " +
                                "directory is requested. [index.html " +
                                "index.pt]")
        parser_.add_option("-e", "--extensions", dest="extensions",
                           help="File extensions that indicate page " +
                                "templates. [pt]")
        parser_.add_option("-m", "--mode", dest="mode",
                           help="`development' or `deployment'. [deployment]")
        opts, args = parser_.parse_args()

        path = os.path.realpath(opts.path)
        if not os.path.isfile(path):
            raise ConfigError("The path %s does not point to a file." % path)

        d = {}

        return (self._validate('opts', d), path)


    def _file(self, path):

        d = {}

        parser_ = RawConfigParser()
        parser_.read(path)

        if parser_.has_section('server'):
            d.update(dict(parser_.items('server')))
        if parser_.has_section('handler'):
            d.update(dict(parser_.items('handler')))

        return self._validate('file', d)


    def _validate(self, context, d):
        """Given a config context and a dictionary, validate the values.

        Some type coercion is performed. If the value can't be coerced, then
        ConfigurationError is raised. Superfluous keys are deleted.

        """

        # port
        # ====
        # Coerce to int. Must be between 0 and 65535.

        errmsg = "[%s] Port must be an integer between 0 and 65535." % context

        if isinstance(d['port'], basestring) and \
           d['port'].isdigit():
            d['port'] = int(d['port'])
        elif isinstance(d['port'], int):
            pass # already an int for some reason (called interactively?)
        else:
            raise ConfigError(errmsg)

        if not(0 <= d['port'] <= 65535):
            raise ConfigError(errmsg)


        # Made it!
        # ========

        return d

        """
        ### just code storage atm


        handler['defaults'] = tuple(handler['defaults'].split())
        handler['extensions'] = tuple(handler['extensions'].split())
        if handler['mode'].lower() not in ('development', 'deployment'):
            raise Usage("Configuration error: mode must be one of `development' " +
                        "and `deployment'.")
        if not os.path.isdir(handler['root']):
            raise Usage("Configuration error: site root is not a directory:" +
                        handler['root'])

            handler['defaults'] = tuple(handler['defaults'].split())
            handler['extensions'] = tuple(handler['extensions'].split())
            if not os.path.isdir(handler['root']):
                raise Usage("Configuration error: site root is not a directory:" +
                            handler['root'])
            return (server, handler)

        """


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:

        # Parse our configuration file.
        # =============================

        config = Configuration(argv)


        # Stop, drop, and roll.
        # =====================

        server = http_server.http_server(**config.server)
        server.install_handler(handler(**config.handler))
        asyncore.loop()


    except ConfigError, err:
        print >> sys.stderr, err.msg
        print >> sys.stderr, "`man 1 httpy' for usage."
        return 2


if __name__ == "__main__":
    sys.exit(main())
