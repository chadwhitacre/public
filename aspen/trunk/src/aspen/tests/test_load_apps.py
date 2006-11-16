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

def test_basic():
    mk('__', '__/etc', ('__/etc/apps.conf', '/ random:choice'))
    expected = [('/', random.choice)]
    actual = Loader().load_apps()
    assert actual == expected

def test_apps_layer():
    mk('__', '__/etc', ('__/etc/apps.conf', """

        / random:choice
        /foo random:sample
        /foo/bar random:shuffle
        /baz random:seed

        """))
    expected = [ ('/foo/bar', random.shuffle)
               , ('/foo', random.sample)
               , ('/baz', random.seed)
               , ('/', random.choice)
                ]
    actual = Loader().load_apps()
    assert actual == expected


# No apps configured
# ==================

def test_no_magic_directory():
    loader = Loader()
    loader.paths.__ = None
    expected = []
    actual = loader.load_apps()
    assert actual == expected

def test_no_file():
    mk('__', '__/etc')
    expected = []
    actual = Loader().load_apps()
    assert actual == expected

def test_empty_file():
    mk('__', '__/etc', ('__/etc/apps.conf', ''))
    expected = []
    actual = Loader().load_apps()
    assert actual == expected


# Errors
# ======

def test_bad_line():
    mk('__', '__/etc', ('__/etc/apps.conf', 'godisnowhere'))
    err = assert_raises(AppsConfError, Loader().load_apps)
    assert err.msg == "malformed line (no space): godisnowhere"

def test_bad_urlpath():
    mk('__', '__/etc', ('__/etc/apps.conf', 'foo string:digits'))
    err = assert_raises(AppsConfError, Loader().load_apps)
    assert err.msg == "URL path not specified absolutely: foo"

def test_not_callable():
    mk('__', '__/etc', ('__/etc/apps.conf', '/ string:digits'))
    err = assert_raises(AppsConfError, Loader().load_apps)
    assert err.msg == "'string:digits' is not callable"

def test_contested_url_path():
    mk('__', '__/etc', ('__/etc/apps.conf', '/ random:choice\n/ random:seed'))
    err = assert_raises(AppsConfError, Loader().load_apps)
    assert err.msg == "URL path is contested: '/'"


# App on fs
# =========

def test_directory_created():
    mk('__', '__/etc', ('__/etc/apps.conf', '/foo random:choice'))
    Loader().load_apps()
    assert os.path.isdir('fsfix/foo')

def test_readme_created():
    mk('__', '__/etc', ('__/etc/apps.conf', '/foo random:choice'))
    Loader().load_apps()
    assert os.path.isfile('fsfix/foo/README.aspen')

def test_readme_contents():
    mk('__', '__/etc', ('__/etc/apps.conf', '/foo random:choice'))
    Loader().load_apps()
    expected = """\
This directory is served by the application configured on line 1 of
__/etc/apps.conf. To wit:

/foo random:choice

"""
    actual = open('fsfix/foo/README.aspen').read()
    assert actual == expected


# Basics
# ======

def test_blank_lines_skipped():
    mk('__', '__/etc', ('__/etc/apps.conf', '\n\n/ random:choice\n\n'))
    expected = [('/', random.choice)]
    actual = Loader().load_apps()
    assert actual == expected

def test_comments_ignored():
    mk('__', '__/etc', ('__/etc/apps.conf', """\
#comment
/foo random:choice#comment
/bar random:sample # comments"""))
    expected = [('/foo', random.choice), ('/bar', random.sample)]
    actual = Loader().load_apps()
    assert actual == expected


# Remove the filesystem fixture after each test.
# ==============================================

globals_ = globals()
for name in dir():
    if name.startswith('test_'):
        globals_[name].teardown = rm
