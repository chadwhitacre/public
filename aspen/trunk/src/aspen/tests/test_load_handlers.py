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

simplate = load.Handler(rulefuncs, handlers.Simplate)
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
    assert actual == expected


# No handlers configured
# ======================
# Should get defaults in each instance

def test_no_magic_directory():
    loader = Loader()
    loader.paths.__ = None
    expected = DEFAULTS
    actual = loader.load_handlers()
    assert actual == expected

def test_no_file():
    mk('__', '__/etc')
    expected = DEFAULTS
    actual = Loader().load_handlers()
    assert actual == expected

def test_empty_file():
    mk('__', '__/etc', ('__/etc/handlers.conf', ''))
    expected = DEFAULTS
    actual = Loader().load_handlers()
    assert actual == expected


if 0:
    # Errors
    # ======

    def test_bad_line():
        mk('__', '__/etc', ('__/etc/apps.conf', 'godisnowhere'))
        err = assert_raises(AppsConfError, Loader().load_handlers)
        assert err.msg == "malformed line (no space): godisnowhere"

    def test_bad_urlpath():
        mk('__', '__/etc', ('__/etc/apps.conf', 'foo string:digits'))
        err = assert_raises(AppsConfError, Loader().load_handlers)
        assert err.msg == "URL path not specified absolutely: foo"

    def test_not_callable():
        mk('__', '__/etc', ('__/etc/apps.conf', '/ string:digits'))
        err = assert_raises(AppsConfError, Loader().load_handlers)
        assert err.msg == "'string:digits' is not callable"

    def test_contested_url_path():
        mk('__', '__/etc', ('__/etc/apps.conf', '/ random:choice\n/ random:seed'))
        err = assert_raises(AppsConfError, Loader().load_handlers)
        assert err.msg == "URL path is contested: '/'"



# Basics
# ======

if 0:
    def test_blank_lines_skipped():
        mk('__', '__/etc', ('__/etc/handlers.conf', '\n\n/ random:choice\n\n'))
        expected = [('/', random.choice)]
        actual = Loader().load_handlers()
        assert actual == expected

    def test_comments_ignored():
        mk('__', '__/etc', ('__/etc/handlers.conf', """\

            #comment
            /foo random:choice#comment
            /bar random:sample # comments

            """))
        expected = [('/foo', random.choice), ('/bar', random.sample)]
        actual = Loader().load_handlers()
        assert actual == expected


# Remove the filesystem fixture after each test.
# ==============================================

globals_ = globals()
for name in dir():
    if name.startswith('test_'):
        globals_[name].teardown = rm
