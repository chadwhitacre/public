import os
import sys

from aspen import load
from aspen.tests import assert_raises
from aspen.tests.fsfixture import build, destroy, convert_path
from aspen.exceptions import *


# Fixture
# =======

lib_python = '__/lib/python'+sys.version[:3]
path = os.path.realpath(convert_path('root/'+lib_python))
sys.path.insert(0, path)

class Paths:
    pass

def Loader():
    """Convenience constructor.
    """
    loader = load.Mixin()
    loader.paths = Paths()
    loader.paths.root = os.path.realpath('root')
    loader.paths.__ = os.path.realpath('root/__')
    return loader


# Apps
# ====

def test_no_magic_directory():
    loader = Loader()
    loader.paths.__ = None
    expected = []
    actual = loader.load_apps()
    assert expected == actual


def test_no_file():
    loader = Loader()
    expected = []
    actual = loader.load_apps()
    assert expected == actual

test_no_file.setup = build(['__', '__/etc'])
test_no_file.teardown = destroy


def test_empty_file():
    loader = Loader()
    expected = []
    actual = loader.load_apps()
    assert expected == actual

test_empty_file.setup = build(['__', '__/etc', ('__/etc/apps.conf', '')])
test_empty_file.teardown = destroy


def test_something():
    loader = Loader()
    from random import choice
    expected = [('/', choice)]
    actual = loader.load_apps()
    assert expected == actual

test_something.setup = build(
  ['__', '__/etc', ('__/etc/apps.conf', '/ random:choice')])
test_something.teardown = destroy


def test_must_be_callable():
    loader = Loader()
    assert_raises(AppsConfError, loader.load_apps)

test_must_be_callable.setup = build(
  ['__', '__/etc', ('__/etc/apps.conf', '/ string:digits')])
test_must_be_callable.teardown = destroy


def test_blank_lines_skipped():
    loader = Loader()
    from random import choice
    expected = [('/', choice)]
    actual = loader.load_apps()
    assert expected == actual

test_blank_lines_skipped.setup = build(
  ['__', '__/etc', ('__/etc/apps.conf', '\n\n/ random:choice\n\n')])
test_blank_lines_skipped.teardown = destroy


def test_comments_ignored():
    loader = Loader()
    from random import choice, sample
    expected = [('/foo', sample), ('/bar', choice)]
    actual = loader.load_apps()
    assert expected == actual

test_comments_ignored.setup = build(
  ['__', '__/etc', ('__/etc/apps.conf', """
#comment
/foo random:choice#comment
/bar random:sample # comments
""")])
test_comments_ignored.teardown = destroy

