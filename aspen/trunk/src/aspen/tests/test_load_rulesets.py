import os

from aspen import load
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


# Working
# =======

if 0:
    def test_basic():
        mk('__', '__/etc', ('__/etc/handlers.conf', """

            fnmatch aspen.rules:fnmatch

            [random:choice]
            fnmatch *

            """))
        expected = []
        actual = Loader().load_rulesets()
        assert actual == expected


# No handlers configured
# ======================
# Should get defaults.

if 0:
    def test_no_magic_directory():
        loader = Loader()
        loader.paths.__ = None
        expected = []
        actual = loader.load_rulesets()
        assert actual == expected

    def test_no_file():
        mk('__', '__/etc')
        expected = []
        actual = Loader().load_rulesets()
        assert actual == expected

    def test_empty_file():
        mk('__', '__/etc', ('__/etc/handlers.conf', ''))
        expected = []
        actual = Loader().load_rulesets()
        assert actual == expected


if 0:
    # Errors
    # ======

    def test_bad_line():
        mk('__', '__/etc', ('__/etc/apps.conf', 'godisnowhere'))
        err = assert_raises(AppsConfError, Loader().load_rulesets)
        assert err.msg == "malformed line (no space): godisnowhere"

    def test_bad_urlpath():
        mk('__', '__/etc', ('__/etc/apps.conf', 'foo string:digits'))
        err = assert_raises(AppsConfError, Loader().load_rulesets)
        assert err.msg == "URL path not specified absolutely: foo"

    def test_not_callable():
        mk('__', '__/etc', ('__/etc/apps.conf', '/ string:digits'))
        err = assert_raises(AppsConfError, Loader().load_rulesets)
        assert err.msg == "'string:digits' is not callable"

    def test_contested_url_path():
        mk('__', '__/etc', ('__/etc/apps.conf', '/ random:choice\n/ random:seed'))
        err = assert_raises(AppsConfError, Loader().load_rulesets)
        assert err.msg == "URL path is contested: '/'"



# Basics
# ======

if 0:
    def test_blank_lines_skipped():
        mk('__', '__/etc', ('__/etc/handlers.conf', '\n\n/ random:choice\n\n'))
        expected = [('/', random.choice)]
        actual = Loader().load_rulesets()
        assert actual == expected

    def test_comments_ignored():
        mk('__', '__/etc', ('__/etc/handlers.conf', """\

            #comment
            /foo random:choice#comment
            /bar random:sample # comments

            """))
        expected = [('/foo', random.choice), ('/bar', random.sample)]
        actual = Loader().load_rulesets()
        assert actual == expected


# Remove the filesystem fixture after each test.
# ==============================================

globals_ = globals()
for name in dir():
    if name.startswith('test_'):
        globals_[name].teardown = rm
