import logging
import os
import sys
import threading
from os.path import exists, isdir

from aspen import load, mode, utils
from aspen.exceptions import HandlerError
from aspen.httpy import Response


log = logging.getLogger('aspen.website')
reloading = threading.Lock()


class Website(load.Mixin):
    """Represent a website for aspen to publish.
    """

    def __init__(self, config):
        self.config = config
        self.paths = config.paths
        self.defaults = config.defaults
        self.load()


    def load(self):
        """Set apps, middleware, and handler rulesets on self.

        Eventually this should maybe respond to SIGHUP or something?

        """
        reloading.acquire()
        try: # critical section
            self.apps = self.load_apps()
            self.rulesets = self.load_rulesets()
        finally:
            reloading.release()


    def on_startup(self):
        """Call startup hook on all WSGI middleware and apps.
        """
        pass


    # Main Dispatcher
    # ===============

    def __call__(self, environ, start_response):
        """Main WSGI callable.
        """

        # Translate the request to the filesystem.
        # ========================================

        fspath = utils.translate(self.paths.root, environ['PATH_INFO'])
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
            utils.check_trailing_slash(environ)
            fspath = utils.find_default(self.defaults, fspath) # 403

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
                environ['PATH_TRANSLATED'] = utils.translate( self.paths.root
                                                            , app_urlpath
                                                             )
                if not isdir(environ['PATH_TRANSLATED']):
                    raise Response(404)
                if app_urlpath.endswith('/'):
                    check_trailing_slash(environ)
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
