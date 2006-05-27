#!/usr/local/bin/python
"""A basic server using the httpy library.
"""
import mimetypes
import rfc822
import os
import stat
import sys
import time

from httpy import Response
from httpy.couplers.standalone import StandAlone
from httpy.couplers.standalone.utils import ConfigError, configure
from httpy.utils import mode


class Responder:

    root = ''       # The document publishing root on the filesystem.
    defaults = None # A sequence of names to consider to be default resources.

    def __init__(self):
        """
        """
        self.root = os.getcwd()
        self.defaults = ['index.html', 'index.htm']


    def respond(self, request):
        """Serve a static file off of the filesystem.

        In staging and deployment modes, we honor any 'If-Modified-Since'
        header, an HTTP header used for caching.

        """

        translated = self.translate(request.path)
        ims = request.headers.get('If-Modified-Since', '')


        # Get basic info from the filesystem and start building a response.
        # =================================================================

        stats = os.stat(translated)
        mtime = stats[stat.ST_MTIME]
        size = stats[stat.ST_SIZE]
        content_type = mimetypes.guess_type(translated)[0] or 'text/plain'
        response = Response(200)


        # Support 304s, but only in deployment mode.
        # ==========================================

        if mode.IS_DEPLOYMENT or mode.IS_STAGING:
            if ims:
                mod_since = rfc822.parsedate(ims)
                last_modified = time.gmtime(mtime)
                if last_modified[:6] <= mod_since[:6]:
                    response.code = 304


        # Finish building the response and return it.
        # ===========================================

        response.headers['Last-Modified'] = rfc822.formatdate(mtime)
        response.headers['Content-Type'] = content_type
        response.headers['Content-Length'] = size
        if response.code != 304:
            response.body = open(translated).read()
        return response


    def translate(self, uri_path):
        """Translate a requested URI to the filesystem.

        Takes a URI path, which is taken to be rooted in self.root. If the
        requested path points to a directory, we ensure that the URI ends with a
        slash, and we look for a default resource per self.defaults. If the URI
        points to a file, we make sure the file exists.

        This method can raise the following Responses:

            301 Moved Permanently
            403 Forbidden
            404 Not Found

        If successful, we return the filesystem path to the particular resource.

        """

        # Knit the requested URI onto the filesystem path.
        # ================================================

        _parts = [self.root] + uri_path.lstrip('/').split('/')
        fs_path = os.sep.join(_parts)
        fs_path = os.path.realpath(fs_path)


        # Interpret it.
        # =============

        if os.path.isdir(fs_path):

            # Process the request as a directory.
            # ===================================

            if not uri_path.endswith('/'):
                # redirect directory requests to trailing slash
                new_location = '%s/' % uri_path
                response = Response(301)
                response.headers['Location'] = new_location
                raise response

            default = None
            for name in self.defaults:
                _path = os.path.join(fs_path, name)
                if os.path.isfile(_path):
                    default = _path
                    break
            if default is None:
                raise Response(403)
            fs_path = default

        else:

            # Process the request as a file.
            # ==============================

            if not os.path.exists(fs_path):
                raise Response(404)


        return fs_path


if __name__ == '__main__':

    try:
        address, threads, uid = configure()
    except ConfigError, err:
        print >> sys.stderr, err.msg
        raise SystemExit(2)

    coupled = StandAlone(Responder, address, threads, uid)
    coupled.go()