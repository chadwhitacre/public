import asyncore
import os
import re
import stat
import sys
from mimetypes import guess_type
from traceback import format_exc
from urllib import unquote
from urlparse import urlsplit

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

_tmp = (
    "<head>"
  , "    <title>Error response</title>"
  , "</head>"
  , "<body>"
  , "    <h1>Error response</h1>"
  , "    <p>Error code: %d</p>" # numeric code  (404)
  , "    <p>Message: %s</p>"   # short message (Not Found)
  , "    %s"                    # long message  (The requested resource was
                                #                not found.)
  , "</body>"
   )
http_server.http_request.DEFAULT_ERROR_MESSAGE = os.linesep.join(_tmp)

LAST_RESORT = """\
<head>
    <title>Error response</title>
</head>
<body>
    <h1>Error response</h1>
    <p>Error code: 500</p>
    <p>Message: Internal Server Error [critical]</p>
    %s
</body>"""


class RequestError(Exception):
    """An error with a request.
    """
    def __init__(self, code_, message=''):
        self.code = code_
        self.msg = http_server.http_request.responses.get(code_)
        self.message = message
        Exception.__init__(self)

    def __str__(self):
        return '%s %s' % (self.code, self.msg)

class Redirect(RequestError):
    """A convenience class for triggering redirects.
    """
    def __init__(self, new_location='/', permanent=False):
        self.new_location = new_location
        code_ = permanent and 301 or 302
        RequestError.__init__(self, code_)


# Define our request handler.
# ===========================

class Handler:
    """An HTTP request handler for use with Medusa.

    Here is a tree showing how requests are processed:

        handle_request
            _handle_request_safely
                _handle_request_unsafely
                    _setpath
                    _getstatic
                    _gettemplate
                        _getframe
                _geterror

    In general, by the end of the flow we will have have a content body,
    and a request object with headers and other attrs set.

    """

    # I assume these are Medusa boilerplate
    IDENT = 'Default HTTP Request Handler'
    def match (self, request):
        # always match, since this is a default
        return 1

    # these at least appear in this file
    valid_commands = ['GET', 'HEAD']
    producer = producers.simple_producer

    def __init__(self, root, defaults, extensions, mode):

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
        content = self._handle_request_safely(request)
        if content and (request.command == 'GET'):
            request.push(self.producer(content))
        request.done()


    def _handle_request_safely(self, request):
        """Given a request, process it safely.

        This is much more likely to return something to serve than *unsafely.

        """

        try:
            # Try to process the request normally.
            content = self._handle_request_unsafely(request)

        except RequestError, error:

            try:
                # Return a nicely formatted error message.
                content = self._geterror(request, error)

            except:
                # There was a problem with _geterror. Help!
                if self.mode == 'development':
                    traceback_ = format_exc()
                else:
                    traceback_ = ''
                content = LAST_RESORT % traceback_
                request['Content-Length'] = long(len(content))
                request['Content-Type'] = 'text/html'
                request.reply_code = 500

        return content


    def _handle_request_unsafely(self, request):
        """Process a request, raising RequestError if there is an error.
        """

        try:

            # Validate the command and add `path' to the request.
            # ===================================================

            if request.command not in self.valid_commands:
                raise RequestError(501) # Not Implemented

            self._setpath(request) # This can raise 301, 400, 403, or 404.


            # Serve the resource.
            # ===================

            ext = None
            if '.' in request.path:
                ext = request.path.split('.')[-1]

            if ext not in self.extensions:
                getter = self._getstatic # This can raise 304.
            else:
                getter = self._gettemplate # This can raise anything
                                           # since sites have a hook.
            return getter(request)

        except RequestError:
            raise

        except Exception:
            if self.mode == 'development':
                traceback_ = format_exc()
            else:
                traceback_ = ''
            raise RequestError(500, traceback_) # Internal Server Error




    def _gettemplate(self, request):
        """Process a request for a page template.

        This method can raise anything, since we have a site-specific hook.

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


    def _geterror(self, request, error):
        """Process a RequestError.

        Since this method is complex and therefore error-prone, we wrap it in
        _handle_request_safely.

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

            template = None
            template_path = os.path.join(self.__, 'error.pt')
            if os.path.exists(template_path):
                if not os.stat(template_path)[stat.ST_SIZE]:
                    print "Empty error.pt: %s" % template_path
                else:
                    template = self.templates.getXMLTemplate(template_path)

            if template is None:

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
        """If available, return the macro `frame' from the file `__/frame.pt'.
        """
        frame = None
        frame_path = os.path.join(self.__, 'frame.pt')
        if os.path.exists(frame_path):
            if not os.stat(frame_path)[stat.ST_SIZE]:
                print "Empty frame.pt: %s" % frame_path
            else:
                template = self.templates.getXMLTemplate(frame_path)
                frame = template.macros.get('frame', None)
                if frame is None:
                    print "No macro `frame' in %s" % frame_path
        return frame



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
