"""Routines for loading plugin objects based on config file settings.
"""
import cStringIO
import inspect
import logging
import os
from os.path import isdir, isfile, join, realpath

from aspen import colon, httpy, utils
from aspen.exceptions import *


log = logging.getLogger('aspen.load')
clean = lambda x: x.split('#',1)[0].strip() # clears comments & whitespace
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


class HandlerRuleSet(object):
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


class Mixin:

    # Apps
    # ====

    def load_apps(self):
        """Return a list of (URI path, WSGI application) tuples.
        """

        # Find a config file to parse.
        # ============================

        apps = []

        try:
            if self.paths.__ is None:
                raise NotImplementedError
            path = join(self.paths.__, 'etc', 'apps.conf')
            if not isfile(path):
                raise NotImplementedError
        except NotImplementedError:
            log.info("No apps configured.")
            return apps


        # We have a config file; proceed.
        # ===============================

        fp = open(path)
        lineno = 0
        urlpaths = []

        for line in fp:
            lineno += 1
            original = line # for README.aspen
            line = clean(line)
            if not line:                            # blank line
                continue
            else:                                   # specification
                if ' ' not in line:
                    msg = "malformed line (no space): %s" % line
                    raise AppsConfError(msg, lineno)
                urlpath, name = line.split(None, 1)
                if not urlpath.startswith('/'):
                    msg = "URL path not specified absolutely: %s" % urlpath
                    raise AppsConfError(msg, lineno)

                fspath = utils.translate(self.paths.root, urlpath)
                if not isdir(fspath):
                    os.makedirs(fspath)
                    log.info("created app directory '%s'"% fspath)
                readme = join(fspath, 'README.aspen')
                open(readme, 'w+').write(README_aspen % (lineno, original))

                if urlpath in urlpaths:
                    msg = "URL path is contested: '%s'" % urlpath
                    raise AppsConfError(msg, lineno)
                urlpaths.append(urlpath)

                obj = colon.colonize(name, fp.name, lineno)
                if not callable(obj):
                    msg = "'%s' is not callable" % name
                    raise AppsConfError(msg, lineno)
                apps.append((urlpath, obj))

        apps.sort()
        apps.reverse()
        return apps

        """

        to support line continuations:

        while line.endswith('\'):
            line += line
            lineno += 1

        """


    # Handler Rulesets
    # ================

    def load_rulesets(self):
        """Return a list of HandlerRuleSet instances.
        """

        # Find a config file to parse.
        # ============================

        user_conf = False
        if self.paths.__ is not None:
            path = join(self.paths.__, 'etc', 'handlers.conf')
            if isfile(path):
                user_conf = True

        if user_conf:
            fp = open(path)
        else:
            log.info("No handlers configured; using defaults.")
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
                obj = colon.colonize(name, fp.name, lineno)
                if inspect.isclass(obj):
                    obj = obj(self)
                if not callable(obj):
                    msg = "handler object %s is not callable" % name
                    raise HandlersConfError(msg, lineno)
                ruleset = HandlerRuleSet(rulefuncs, obj, name)
                rulesets.append(ruleset)
                continue
            elif ruleset is None:                   # anonymous section
                rulename, name = line.split(None, 1)
                obj = colon.colonize(name, fp.name, lineno)
                if not callable(obj):
                    msg = "rule %s is not callable" % name
                    raise HandlersConfError(msg, lineno)
                rulefuncs[rulename] = obj
            else:                                   # named section
                ruleset.add(line, lineno)

        return rulesets


    # Middleware
    # ==========

    def load_middleware(self):
        """Return a list of (URI path, WSGI middleware) tuples.
        """

        # Find a config file to parse.
        # ============================

        stack = [httpy.Responder]

        try:
            if self.paths.__ is None:
                raise NotImplementedError
            path = join(self.paths.__, 'etc', 'middleware.conf')
            if not isfile(path):
                raise NotImplementedError
        except NotImplementedError:
            log.info("No middleware configured.")
            return stack


        # We have a config file; proceed.
        # ===============================

        fp = open(path)
        lineno = 0

        for line in fp:
            lineno += 1
            name = clean(line)
            if not name:                            # blank line
                continue
            else:                                   # specification
                obj = colon.colonize(name, fp.name, lineno)
                if not callable(obj):
                    msg = "'%s' is not callable" % name
                    raise MiddlewareConfError(msg, lineno)
                stack.append(obj)

        stack.reverse()
        return stack
