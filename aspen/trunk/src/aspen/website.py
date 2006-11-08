import cStringIO
import inspect
import logging
import os
import string
import sys
import threading
import traceback
from os.path import basename, dirname, exists, isdir, isfile, join

from httpy import Response, mode, utils
from httpy.responders.static import Static

from aspen import * # Error classes


log = logging.getLogger('aspen.website')
clean = lambda x: x.split('#',1)[0].strip() # clears comments & whitespace
reloading = threading.Lock()
default_handlers_conf = """\

    fnmatch     aspen.rules.fnmatch
    hashbang    aspen.rules.hashbang
    mime-type   aspen.rules.mimetype


    [aspen.handlers.HTTP404]
    fnmatch *.py[cod]           # hide any compiled Python scripts


    [aspen.handlers.pyscript]
        fnmatch     *.py        # exec python scripts ...
    OR  hashbang                # ... and anything with a hashbang


    [aspen.handlers.Simplate]
    mime-type text/html         # run html files through the Simplates engine


    [aspen.handlers.static]
    fnmatch *                   # anything else, serve it statically

"""
README_aspen = """\
This directory is served by the application configured on line %d of
__/etc/apps.conf. To wit:

%s

"""


INITIAL = '_' + string.letters
INNER = INITIAL + string.digits
def is_valid_identifier(s):
    """Given a string of length > 0, return a boolean.

        >>> is_valid_identifier('.svn')
        False
        >>> is_valid_identifier('svn')
        True
        >>> is_valid_identifier('_svn')
        True
        >>> is_valid_identifier('__svn')
        True
        >>> is_valid_identifier('123')
        False
        >>> is_valid_identifier('r123')
        True

    """
    try:
        assert s[0] in INITIAL
        assert False not in [x in INNER for x in s]
        return True
    except AssertionError:
        return False

class HandlerRuleSet:
    """Represent the set of rules associated with a handler.

    Some optimization ideas:

      - cache the results of match()
      - evaluate the expression after each rule is added, exit early if False

    """

    handler = None # the handler callable we are tracking
    _rules = None # a list containing the rules

    def __init__(self, rulefuncs, handler, handler_name):
        """Takes a mapping of rulename to rulefunc, and a handler callable.
        """
        self._funcs = rulefuncs
        self.handler = handler
        self.handler_name = handler_name

    def __str__(self):
        return "<RuleSet for %s>" % self.handler_name
    __repr__ = __str__


    def add(self, rule, lineno):
        """Given a rule string, add it to the rules for this handler.

        The first item in self._rules is a two-tuple: (rulename, predicate),
        subsequent items are three-tuples: (boolean, rulename, predicate).

            boolean -- one of 'and', 'or', 'and not'. Any NOT in the conf file
                       becomes 'and not' here.

            rulename -- a name defined in the first (anonymous) section of
                        handlers.conf; maps to a rule callable in self._funcs

            predicate -- a string that is meaningful to the rule callable

        lineno is for error handling.

        """
        if self._rules is None:                 # no rules yet
            parts = rule.split(None, 1)
            if len(parts) != 2:
                msg = "need two tokens in '%s'" % rule
                raise HandlersConfError(msg, lineno)
            rulename, predicate = parts
            if rulename not in self._funcs:
                msg = "no rule named '%s'" % rulename
                raise HandlersConfError(msg, lineno)
            self._rules = [(rulename, predicate)]
        else:                                   # we have at least one rule
            parts = rule.split(None, 2)
            if len(parts) not in (2,3):
                msg = "need two or three tokens in '%s'" % rule
                raise HandlersConfError(msg, lineno)
            parts.reverse()

            orig = parts.pop()
            boolean = orig.lower()
            if boolean not in ('and', 'or', 'not'):
                msg = "bad boolean '%s' in '%s'" % (orig, rule)
                raise HandlersConfError(msg, lineno)
            boolean = (boolean == 'not') and 'and not' or boolean

            rulename = parts.pop()
            if rulename not in self._funcs:
                msg = "no rule named '%s'" % rulename
                raise HandlersConfError(msg, lineno)

            predicate = parts and parts.pop() or None

            self._rules.append((boolean, rulename, predicate))


    def match(self, fp):
        """Given a file pointer (positioned at 0), return a boolean.

        I thought of allowing rules to return arbitrary values that would then
        be passed along to the handlers. Basically this was to support routes-
        style regular expression matching, but that is an application use case,
        and handlers are specifically not for applications but publications.

        """
        if not self._rules: # None or []
            raise HandlerError, "no rules to match"

        rulename, predicate = self._rules[0]                    # first
        expressions = [str(self._funcs[rulename](fp, predicate))]

        for boolean, rulename, predicate in self._rules[1:]:    # subsequent
            fp.seek(0)
            result = bool(self._funcs[rulename](fp, predicate))
            expressions.append('%s %s' % (boolean, result))

        expression = ' '.join(expressions)
        return eval(expression) # e.g.: True or False and not True

class Website:
    """Represent a website for aspen to publish.
    """

    def __init__(self, paths):
        self.paths = paths
        self.static = Static()
        self.static.root = self.paths.root
        self.static.defaults = ['index.htm', 'index.html', 'index.py']
        self.__configure()


    def __configure(self):
        """Set hooks and handlers on self.

        Eventually this should maybe respond to SIGHUP.

        """
        reloading.acquire()
        try: # critical section
            self.__hooks = self.__load_hooks()
            self.__rulesets = self.__load_rulesets()
            self.__apps = self.__load_apps()
            self.__on_startup()
        finally:
            reloading.release()


    def respond(self, request):
        """Given a Request, return a response (w/ error handling).
        """

        # Reload hooks and handlers in dev mode.
        # ======================================

        if mode.IS_DEVELOPMENT or mode.IS_DEBUGGING:
            self.__configure()


        # Handle safely.
        # ==============
        # All hooks (besides startup) are called here.

        try:
            request = self.__on_request(request)
            response = self.__respond_unsafely(request)
        except Response, response:
            pass
        except:
            response = self.__on_exception(request)
            raise response

        return self.__on_response(request, response)


    def __respond_unsafely(self, request):
        """Given a Request, return a response (w/o error handling).
        """

        # Translate the request to the filesystem.
        # ========================================

        fspath = self.static.translate(request.path)
        if self.paths.__ is not None:
            if fspath.startswith(self.paths.__): # protect magic directory
                raise Response(404)


        # See if any known application claims this request.
        # =================================================

        app = self.__get_app(request, fspath) # may redirect
        if app is not None:
            response = app.respond(request)
        else:

            # No app wants it. Get a resource and a handler.
            # ==============================================

            fspath = self.static.validate(request.path, fspath) # 404 or 301
            fspath = self.static.find_default(fspath) # may raise 403
            fp = open(fspath)
            handler = self.__get_handler(fp)
            fp.seek(0)


            # Set up the context and then call the handler.
            # =============================================
            # Session and page/conversation contexts (SEAM) should be added by
            # hooks.

            context = dict(website=self)                # eternal
            context['fp'] = fp                          # ephemeral
            context['request'] = request
            context['response'] = Response()
            #context['cookie'] = Cookie(request)
            #context['form'] = Form(request)
            #context['query'] = Query(request)

            response = handler.handle(**context)

        return response


    # Hooks
    # =====

    def __load_hooks(self):
        """Return a mapping of hook names to lists of callables.

        This method parses the __/etc/hooks.conf file, which is a list of Python
        dotted names, split into 5 sections. Section names are given in
        brackets, and are taken from the hook names:

            exception
            request
            response
            startup

        Lines after each section name are taken to be Python dotted names
        specifying objects that should be called at each hook point. Objects are
        called in the order specified. If an object cannot be found, ImportError
        is raised.

        Preceding the first explicitly-named section is an anonymous section,
        where names are interpreted as module or package names from which should
        be imported objects with names corresponding to each hook. Callables
        specified in this manner are called in forward order for the startup and
        request hooks, and in reverse order for the response and exception
        hooks. Modules need not define a callable for every hook.

        The comment character for this file is #, and comments can be included
        in-line. Blank lines are ignored, as is initial and trailing whitespace
        per-line.

        Example file:

            foo.hooks   # will look for {exception,request,response,startup}
            bar.hooks   #   in these modules/objects

            [startup]
              example.hooks.startup

            [exception]
              OtherExample.ExceptionHandling.hook

        """

        # Set up some variables; exit early if we can.
        # ============================================

        hooks = { 'exception'   : []
                , 'request'     : []
                , 'response'    : []
                , 'startup'     : []
                 }

        if self.paths.__ is None:
            return hooks

        path = join(self.paths.__, 'etc', 'hooks.conf')
        if not isfile(path):
            return hooks


        # We have a config file; proceed.
        # ===============================

        fp = open(path)
        hook = None
        lineno = 0

        for line in fp:
            lineno += 1
            line = clean(line)
            if not line:                            # blank line
                continue
            elif line.startswith('['):              # new section
                if not line.endswith(']'):
                    raise HooksConfError("missing end-bracket", lineno)
                hook = line[1:-1].lower()
                if hook and (hook not in hooks):
                    raise HooksConfError("bad hook '%s'" % hook, lineno)
                continue
            elif hook is None:                      # anonymous section
                at_least_one = False
                obj = self.__import(line, HooksConfError, lineno)
                for name in hooks:
                    callable_ = getattr(obj, name, None)
                    if callable_ is None:
                        log.info('no %s hook in %s' % (name, line))
                        continue
                    at_least_one = True
                    if name in ('startup', 'request'):
                        hooks[name].append(callable_)
                    else:
                        hooks[name].insert(0, callable_)
                if not at_least_one:
                    log.warn('%s provides no hooks' % line)
            else:                                   # named section
                callable_ = self.__import(line, HooksConfError, lineno)
                if not callable(callable_):
                    msg = "%s is not callable" % line
                    raise HooksConfError(msg, lineno)
                hooks[hook].append(callable_)

        return hooks


    def __on_startup(website):
        if website.__hooks['startup'] is not None:
            for func in website.__hooks['startup']:
                func(website)


    def __on_request(website, request):
        if website.__hooks['request'] is not None:
            for func in website.__hooks['request']:
                request = func(website, request)
                if request is None:
                    raise HookError, "A request hook returned None."
        return request


    def __on_response(website, request, response):
        if website.__hooks['response'] is not None:
            for func in website.__hooks['response']:
                response = func(website, request, response)
                if response is None:
                    raise HookError, "A response hook returned None."
        return response


    def __on_exception(website, request):
        response = Response(500)
        if mode.IS_DEBUGGING or mode.IS_DEVELOPMENT:
            response.body = traceback.format_exc()
        if website.__hooks['exception'] is not None:
            for func in website.__hooks['exception']:
                response = func(website, request, response)
                if response is None:
                    raise HookError, "An exception hook returned None."
        return response


    # Handler Rule Sets
    # =================

    def __load_rulesets(self):
        """Return a list of HandlerRuleSet instances.

        This method parses the __/etc/handlers.conf file. This file begins with
        a newline-separated list of white-space-separated rule name/object name
        pairs. The rule names can be any string without whitespace.

        Each object name must specify a Python class, instance, module, or
        function in dotted notation. In each case we are looking for a callable
        that takes a file object (positioned at 0) and an arbitrary predicate
        string, and returns a boolean. Here's how each is treated:

            class -- instantiated with the website instance as a positional
                     argument; a 'rule' attribute is the callable

            instance/module -- a 'rule' attribute is the callable

            function -- the function itself is the callable


        If the object name has no dots, it is imported as a module/package. If
        it does contain dots, then the last name becomes the 'import' target, and
        the remaining dotted portion becomes the 'from' target.

            aspen.handlers.static => from aspen.handlers import static


        The comment character for this file is #, and comments can be included
        in-line. Blank lines are ignored, as is initial and trailing whitespace
        per-line.

        Example (this is Aspen's default handlers configuration):

            %s


        If the file __/etc/handlers.conf exists at all, these defaults
        disappear, and you must respecify these rules in your own file if you
        want them.

        """ % default_handlers_conf


        # Find a conf file to parse.
        # ==========================

        user_conf = False
        if self.paths.__ is not None:
            path = join(self.paths.__, 'etc', 'handlers.conf')
            if isfile(path):
                user_conf = True

        if user_conf:
            fp = open(path)
        else:
            fp = cStringIO.StringIO(default_handlers_conf)


        # We have a config file; proceed.
        # ===============================
        # The conditions in the loop below are not in the order found in the
        # file, but are in the order necessary for correct processing.

        rulefuncs = {} # a mapping of function names to rule functions
        rulesets = [] # a list of HandlerRuleSet objects
        ruleset = None # the HandlerRuleSet we are currently processing
        lineno = 0

        for line in fp:
            lineno += 1
            line = clean(line)
            if not line:                            # blank line
                continue
            elif line.startswith('['):              # new section
                if not line.endswith(']'):
                    raise HandlersConfError("missing end-bracket", lineno)
                name = line[1:-1]
                obj = self.__import(name, HandlersConfError, lineno)
                msg = ''
                if inspect.isfunction(obj):
                    obj.handle = obj
                elif not hasattr(obj, 'handle'):
                    msg = "handler object at %s has no 'handle' callable" % name
                elif not callable(obj.handle):
                    msg = "'handle' attribute of %s is not callable" % name
                if msg:
                    raise HandlersConfError(msg, lineno)
                ruleset = HandlerRuleSet(rulefuncs, obj, name)
                rulesets.append(ruleset)
                continue
            elif ruleset is None:                   # anonymous section
                rulename, name = line.split(None, 1)
                obj = self.__import(name, HandlersConfError, lineno)
                msg = ''
                if inspect.isfunction(obj):
                    obj.rule = obj
                elif not hasattr(obj, 'rule'):
                    msg = "rule object at %s has no 'rule' callable" % name
                elif not callable(obj.rule):
                    msg = "'rule' attribute of %s is not callable" % name
                if msg:
                    raise HandlersConfError(msg, lineno)
                rulefuncs[rulename] = obj.rule
            else:                                   # named section
                ruleset.add(line, lineno)

        return rulesets


    def __get_handler(self, fp):
        """Given a filesystem path, return the first matching handler.
        """
        handler = None
        for ruleset in self.__rulesets:
            fp.seek(0)
            if ruleset.match(fp):
                handler = ruleset.handler
                break
        if handler is None:
            log.warn("No handler found for filesystem path '%s'" % fspath)
            raise HandlerError("No handler found.")
        return handler


    # Apps
    # ====

    def __load_apps(self):
        """Return a list of (URI paths, application callable) tuples.

        This method parses the __/etc/apps.conf file. This file contains a
        newline-separated list of white-space-separated path name/object name
        pairs. The path names refer to URL-space, but must be reflected on the
        filesystem. If the trailing slash is given, then requests for that
        directory will first be redirected to the trailing slash before being
        handed off to the application. If no trailing slash is given, the
        application will also get requests w/o the slash. Applications match in
        the order specified.

        Each object name must specify a Python class, instance, module, or
        function in dotted notation. In each case we are looking for a callable
        that takes a request object and returns a response object. Here's how
        each is treated:

            class -- instantiated with the website instance as a positional
                     argument; a 'respond' attribute is the callable

            instance/module -- a 'respond' attribute is the callable

            function -- the function itself is the callable


        If the object name has no dots, it is imported as a module/package. If
        it does contain dots, then the last name becomes the 'import' target, and
        the remaining dotted portion becomes the 'from' target.

            example.apps.foo => from example.apps import foo


        The comment character for this file is #, and comments can be included
        in-line. Blank lines are ignored, as is initial and trailing whitespace
        per-line.

        Example:

            /foo        example.apps.foo    # will get both /foo and /foo/
            /bar/       example.apps.bar    # /bar will redirect to /bar/
            /bar        example.apps.Bar    # will never be called
            /bar/baz    example.apps.baz    # also never called


        If it doesn't already exist, aspen will place a file called README.aspen
        in each directory mentioned in apps.conf, containing the relevant line
        from apps.conf. If the directory does not exist, we raise AppsConfError.

        """

        # Find a conf file to parse.
        # ==========================

        apps = []

        if self.paths.__ is None:
            return apps

        path = join(self.paths.__, 'etc', 'apps.conf')
        if not isfile(path):
            return apps


        # We have a config file; proceed.
        # ===============================
        # The conditions in the loop below are not in the order found in the
        # file, but are in the order necessary for correct processing.

        fp = open(path)
        lineno = 0

        for line in fp:
            lineno += 1
            original = line # for README.aspen
            line = clean(line)
            if not line:                            # blank line
                continue
            else:                                   # specification
                urlpath, name = line.split(None, 1)
                if not urlpath.startswith('/'):
                    msg = "URL path not specified absolutely: %s" % line
                    raise AppsConfError(msg, lineno)
                fspath = self.static.translate(urlpath)
                if not isdir(fspath):
                    msg = "%s does not point to a directory" % fspath
                    raise AppsConfError(msg, lineno)
                readme = join(fspath, 'README.aspen')
                open(readme, 'w+').write(README_aspen % (lineno, original))

                obj = self.__import(name, AppsConfError, lineno)
                msg = ''
                if inspect.isfunction(obj):
                    obj.respond = obj
                elif not hasattr(obj, 'respond'):
                    msg = "app object at %s has no 'respond' callable" % name
                elif not callable(obj.respond):
                    msg = "'respond' attribute of %s is not callable" % name
                if msg:
                    raise AppsConfError(msg, lineno)

                obj.urlpath = urlpath
                apps.append((urlpath, obj))

        return apps


    def __get_app(self, request, fspath):
        """Given a request, return the first matching app.
        """
        app = None
        for urlpath, _app in self.__apps:
            if request.path.startswith(urlpath):
                dirpath = self.static.translate(urlpath)
                if not isdir(dirpath):       # always check for existence
                    raise Response(404)
                if urlpath.endswith('/'):   # sometimes check for trailing slash
                    self.static.validate(request.path, dirpath) # may raise 301
                app = _app
                break
        if app is None:
            log.debug("No app found for '%s'" % request.path)
        return app


    # Import helpers
    # ==============

    def __import(self, name, Err, lineno=None):
        """Given a dotted name and some error helpers, return an object.

        If Err is None then all ImportErrors are swallowed, and None is
        returned. If Err is not None, the lineno should be the line number of
        the file where the bad import name occurs.

        """
        obj = None
        if Err is None:
            try:
                obj = self.__import_unsafe(name)
            except ImportError:
                pass
        else:
            try:
                obj = self.__import_unsafe(name)
            except ImportError, err:
                raise Err(err.args[0], lineno)
        return obj


    def __import_unsafe(self, name):
        """Import w/o error handling.

        If the imported thing is a class, we instantiate it with the website
        instance as a positional argument.

        """
        if not is_valid_identifier(name.replace('.','')):
            raise ImportError('%s is not a valid Python dotted name.' % name)
        if '.' not in name:
            exec 'import %s as obj'
        else:
            modname, objname = name.rsplit('.', 1)
            exec 'from %s import %s as obj' % (modname, objname)
        if inspect.isclass(obj):
            obj = obj(self)
        return obj

if __name__ == '__main__':
    import doctest
    doctest.testmod()
