import os

from aspen import handlers, load, rules
from aspen.tests import assert_raises
from aspen.tests.fsfix import mk, rm
from aspen.exceptions import *


# Fixture
# =======

import random
import string

class Paths:
    pass

def Loader():
    """Convenience constructor.
    """
    loader = load.Mixin()
    loader.paths = Paths()
    loader.paths.root = os.path.realpath('fsfix')
    loader.paths.__ = os.path.realpath('fsfix/__')
    return loader

handler = load.Handler({'fnmatch':rules.fnmatch}, random.choice)
handler.add("fnmatch *", 0)

rulefuncs = dict()
rulefuncs['fnmatch'] = rules.fnmatch
rulefuncs['hashbang'] = rules.hashbang
rulefuncs['mime-type'] = rules.mimetype

http404 = load.Handler(rulefuncs, handlers.HTTP404)
http404.add("fnmatch *.py[cod]", 0)

pyscript = load.Handler(rulefuncs, handlers.pyscript)
pyscript.add("fnmatch *.py", 0)
pyscript.add("OR hashbang", 0)

simplate = load.Handler(rulefuncs, handlers.Simplate(Loader()))
simplate.add("mime-type text/html", 0)

static = load.Handler(rulefuncs, handlers.static)
static.add("fnmatch *", 0)

DEFAULTS = [http404, pyscript, simplate, static]


# Working
# =======

def test_basic():
    mk('__', '__/etc', ('__/etc/handlers.conf', """

        fnmatch aspen.rules:fnmatch

        [random:choice]
        fnmatch *

        """))
    expected = [handler]
    actual = Loader().load_handlers()
    assert actual == expected, actual


# No handlers configured
# ======================
# Should get defaults when there's no file, an empty when there's an empty file.

def test_no_magic_directory():
    loader = Loader()
    loader.paths.__ = None
    expected = DEFAULTS
    actual = loader.load_handlers()
    assert actual == expected, actual

def test_no_file():
    mk('__', '__/etc')
    expected = DEFAULTS
    actual = Loader().load_handlers()
    assert actual == expected, actual

def test_empty_file():
    mk('__', '__/etc', ('__/etc/handlers.conf', ''))
    expected = []
    actual = Loader().load_handlers()
    assert actual == expected, actual


# Errors
# ======

def test_anon_bad_line():
    mk('__', '__/etc', ('__/etc/handlers.conf', 'foo\n[foo]'))
    err = assert_raises(HandlersConfError, Loader().load_handlers)
    assert err.msg == "malformed line (no space): 'foo'", err.msg

def test_anon_not_callable():
    mk('__', '__/etc', ('__/etc/handlers.conf', 'foo string:digits'))
    err = assert_raises(HandlersConfError, Loader().load_handlers)
    assert err.msg == "'string:digits' is not callable", err.msg


def test_section_bad_section_header():
    mk('__', '__/etc', ('__/etc/handlers.conf', '[foo'))
    err = assert_raises(HandlersConfError, Loader().load_handlers)
    assert err.msg == "missing end-bracket", err.msg

def test_section_no_rules_yet():
    mk('__', '__/etc', ('__/etc/handlers.conf', '[foo]'))
    err = assert_raises(HandlersConfError, Loader().load_handlers)
    assert err.msg == "no rules specified yet", err.msg

def test_section_not_callable():
    mk('__', '__/etc', ('__/etc/handlers.conf', """

        foo random:choice

        [string:digits]
        foo

        """))

    err = assert_raises(HandlersConfError, Loader().load_handlers)
    assert err.msg == "'string:digits' is not callable", err.msg




# Basics
# ======

if 0:
    def test_blank_lines_skipped():
        mk('__', '__/etc', ('__/etc/handlers.conf', '\n\n/ random:choice\n\n'))
        expected = [('/', random.choice)]
        actual = Loader().load_handlers()
        assert actual == expected, actual

    def test_comments_ignored():
        mk('__', '__/etc', ('__/etc/handlers.conf', """\

            #comment
            /foo random:choice#comment
            /bar random:sample # comments

            """))
        expected = [('/foo', random.choice), ('/bar', random.sample)]
        actual = Loader().load_handlers()
        assert actual == expected, actual


# Remove the filesystem fixture after each test.
# ==============================================

globals_ = globals()
for name in dir():
    if name.startswith('test_'):
        globals_[name].teardown = rm
