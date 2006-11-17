import os
import sys

from aspen import load
from aspen.tests import assert_raises
from aspen.tests.fsfix import mk, attach_rm
from aspen.exceptions import *


# Fixture
# =======

import random
import string

lib_python = os.path.join('__', 'lib', 'python%s' % sys.version[:3])
sys.path.insert(0, os.path.join('fsfix', lib_python))

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

MODULE = """\
class App:
  def __init__(self, website):
    self.website = website
  def __call__(self, env, start):
    return "Greetings, program!"
"""


# Working
# =======

def test_basic():
    mk('__/etc', ('__/etc/apps.conf', '/ random:choice'))
    expected = [('/', random.choice)]
    actual = Loader().load_apps()
    assert actual == expected, actual

def test_apps_layer():
    mk('__/etc', ('__/etc/apps.conf', """

        /           random:choice
        /foo        random:sample
        /foo/bar    random:shuffle
        /baz/       random:seed

        """))
    expected = [ ('/foo/bar', random.shuffle)
               , ('/foo', random.sample)
               , ('/baz/', random.seed)
               , ('/', random.choice)
                ]
    actual = Loader().load_apps()
    assert actual == expected, actual

def test_classes_instantiated():
    mk( '__/etc', lib_python
      , ('__/etc/apps.conf', '/ TESTING_apps:App')
      , (lib_python+'/TESTING_apps.py', MODULE)
       )
    from TESTING_apps import App as expected
    actual = Loader().load_apps()[0][1].__class__
    assert actual == expected, actual



# No apps configured
# ==================

def test_no_magic_directory():
    loader = Loader()
    loader.paths.__ = None
    expected = []
    actual = loader.load_apps()
    assert actual == expected, actual

def test_no_file():
    mk('__/etc')
    expected = []
    actual = Loader().load_apps()
    assert actual == expected, actual

def test_empty_file():
    mk('__/etc', ('__/etc/apps.conf', ''))
    expected = []
    actual = Loader().load_apps()
    assert actual == expected, actual


# Errors
# ======

def test_bad_line():
    mk('__/etc', ('__/etc/apps.conf', 'godisnowhere'))
    err = assert_raises(AppsConfError, Loader().load_apps)
    assert err.msg == "malformed line (no space): 'godisnowhere'", err.msg

def test_bad_urlpath():
    mk('__/etc', ('__/etc/apps.conf', 'foo string:digits'))
    err = assert_raises(AppsConfError, Loader().load_apps)
    assert err.msg == "URL path not specified absolutely: 'foo'", err.msg

def test_not_callable():
    mk('__/etc', ('__/etc/apps.conf', '/ string:digits'))
    err = assert_raises(AppsConfError, Loader().load_apps)
    assert err.msg == "'string:digits' is not callable", err.msg

def test_contested_url_path():
    mk('__/etc', ('__/etc/apps.conf', """

        /foo random:choice
        /foo random:sample

        """))
    err = assert_raises(AppsConfError, Loader().load_apps)
    assert err.msg == "URL path is contested: '/foo'", err.msg

def test_contested_url_path_trailing_first():
    mk('__/etc', ('__/etc/apps.conf', """

        /foo/ random:choice
        /foo  random:sample

        """))
    err = assert_raises(AppsConfError, Loader().load_apps)
    assert err.msg == "URL path is contested: '/foo'", err.msg

def test_contested_url_path_trailing_second():
    mk('__/etc', ('__/etc/apps.conf', """

        /foo  random:choice
        /foo/ random:sample

        """))
    err = assert_raises(AppsConfError, Loader().load_apps)
    assert err.msg == "URL path is contested: '/foo/'", err.msg


# App on fs
# =========

def test_directory_created():
    mk('__/etc', ('__/etc/apps.conf', '/foo random:choice'))
    Loader().load_apps()
    assert os.path.isdir('fsfix/foo')

def test_readme_created():
    mk('__/etc', ('__/etc/apps.conf', '/foo random:choice'))
    Loader().load_apps()
    assert os.path.isfile('fsfix/foo/README.aspen')

def test_readme_contents():
    mk('__/etc', ('__/etc/apps.conf', '/foo random:choice'))
    Loader().load_apps()
    expected = """\
This directory is served by the application configured on line 1 of
__/etc/apps.conf. To wit:

/foo random:choice

"""
    actual = open('fsfix/foo/README.aspen').read()
    assert actual == expected, actual


# Basics
# ======

def test_blank_lines_skipped():
    mk('__/etc', ('__/etc/apps.conf', '\n\n/ random:choice\n\n'))
    expected = [('/', random.choice)]
    actual = Loader().load_apps()
    assert actual == expected, actual

def test_comments_ignored():
    mk('__/etc', ('__/etc/apps.conf', """\
#comment
/foo random:choice#comment
/bar random:sample # comments"""))
    expected = [('/foo', random.choice), ('/bar', random.sample)]
    actual = Loader().load_apps()
    assert actual == expected, actual


# Remove the filesystem fixture after each test.
# ==============================================

attach_rm(globals(), 'test_')
