import logging
import os
import sys
import threading
from os.path import exists, isdir, isfile, join, realpath

from aspen import mode
from aspen import mixins
from aspen.exceptions import HandlerError
from aspen.response import Response


log = logging.getLogger('aspen.website')
reloading = threading.Lock()

class Website(mixins.AppLoader, mixins.HandlerLoader, mixins.ImportHelpers):
    """Represent a website for aspen to publish.
    """

    def __init__(self, paths):
        self.paths = paths
        self.defaults = ['index.htm', 'index.html', 'index.py'] # XXX: expose this to config
        self.configure()


    def configure(self):
        """Set apps, middleware, and handler rulesets on self.

        Eventually this should maybe respond to SIGHUP.

        """
        reloading.acquire()
        try: # critical section
            self.apps = self.load_apps()
            self.middleware = self.load_middleware()
            self.rulesets = self.load_rulesets()
            self.on_startup()
        finally:
            reloading.release()


    # Flesh out
    # =========

    def load_middleware(self):
        """Load middleware (replaces hooks).
        """
        pass

    def on_startup(self):
        """Call startup hook on all WSGI middleware and apps.
        """
        pass


    # Main Dispatcher
    # ===============

    def __call__(self, environ, start_response):
        """Meets the WSGI contract.

        The request side of WSGI isn't so bad (the "commons" of the environ
        mapping), but the response side is a little stiffer. This shim lets us
        return strings, or return/raise Response objects in addition to the
        usual iterables that WSGI calls for. This is convenient when we don't
        care to call start_response ourselves, which is really designed for
        high-throughput buffering situations.

        """
        try:
            response = self.call_and_response(environ, start_response)
        except Response, response:
            pass
        except:
            raise

        if isinstance(response, Response):
            response = response.to_wsgi(start_response)
        elif isinstance(response, basestring):
            response = [response]

        return response


    def call_and_response(self, environ, start_response):
        """In addition to the WSGI contract, may return or raise a Response.
        """

        # Translate the request to the filesystem.
        # ========================================

        fspath = self.translate(environ['PATH_INFO'])
        if self.paths.__ is not None:
            if fspath.startswith(self.paths.__): # protect magic directory
                raise Response(404)
        environ['PATH_TRANSLATED'] = fspath


        # Dispatch to a WSGI app or an aspen handler.
        # ===========================================

        app = self.get_app(environ) # 301
        if app is not None:                                 # app
            response = app(environ, start_response)
        else:                                               # handler
            if not exists(fspath):
                raise Response(404)
            self.check_trailing_slash(environ)
            fspath = self.find_default(fspath) # 403

            environ['PATH_TRANSLATED'] = fspath
            environ['aspen.website'] = self
            fp = environ['aspen.fp'] = open(fspath)

            handler = self.get_handler(fp)
            fp.seek(0)
            response = handler.handle(environ)

        return response


    # Plugin Retrievers
    # =================
    # Unlike the middleware stack, apps and handlers need to be located
    # per-request.

    def get_app(self, environ):
        """Given WSGI arguments, return the first matching app.
        """
        app = None
        for app_urlpath, _app in self.apps:
            if environ['PATH_INFO'].startswith(app_urlpath):
                environ['PATH_TRANSLATED'] = self.translate(app_urlpath)
                if not isdir(environ['PATH_TRANSLATED']):
                    raise Response(404)
                if app_urlpath.endswith('/'):
                    self.check_trailing_slash(environ)
                app = _app
                break
        if app is None:
            log.debug("No app found for '%s'" % environ['PATH_INFO'])
        return app


    def get_handler(self, fp):
        """Given a filesystem path, return the first matching handler.
        """
        handler = None
        for ruleset in self.rulesets:
            fp.seek(0)
            if ruleset.match(fp):
                handler = ruleset.handler
                break
        if handler is None:
            log.warn("No handler found for filesystem path '%s'" % fp.name)
            raise HandlerError("No handler found.")
        return handler


    # Path Helpers
    # ============

    def translate(self, url):
        """Translate a requested URL to the filesystem.
        """
        parts = [self.paths.root] + url.lstrip('/').split('/')
        return realpath(os.sep.join(parts))


    def check_trailing_slash(self, environ):
        """Given a WSGI environ, return None or raise 301.

        environ must have PATH_TRANSLATED set in addition to PATH_INFO, which is
        required by the spec.

        """
        fs = environ['PATH_TRANSLATED']
        url = environ['PATH_INFO']
        if isdir(fs) and not url.endswith('/'):
            response = Response(301)
            response.headers['Location'] = '%s/' % url
            raise response


    def find_default(self, path):
        """Given a path, return a filepath or raise 403.
        """
        if isdir(path):
            default = None
            for name in self.defaults:
                _path = join(path, name)
                if isfile(_path):
                    default = _path
                    break
            if default is None:
                raise Response(403)
            path = default
        return path
