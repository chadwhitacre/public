import os
import sys

from aspen import load
from aspen.httpy import Responder
from aspen.tests.fsfixture import build, destroy, convert_path
from aspen.exceptions import *


# Fixture
# =======

lib_python = '__/lib/python'+sys.version[:3]
path = os.path.realpath(convert_path('root/'+lib_python))
sys.path.insert(0, path)

class Paths:
    pass

def Loader(__):
    """Convenience constructor.
    """
    loader = load.Mixin()
    loader.paths = Paths()
    loader.paths.__ = __
    return loader


# Tests
# =====

def test_no_magic_directory():
    loader = Loader(None)
    expected = [Responder]
    actual = loader.load_middleware()
    assert expected == actual


def test_no_file():
    loader = Loader('.')
    expected = [Responder]
    actual = loader.load_middleware()
    assert expected == actual


def test_empty_file():
    loader = Loader('.')
    expected = [Responder]
    actual = loader.load_middleware()
    assert expected == actual

test_empty_file.setup = build([('middleware.conf', '')])
test_empty_file.teardown = destroy


def test_something():
    loader = Loader('root/__')
    from random import choice
    expected = [choice, Responder]
    actual = loader.load_middleware()
    assert expected == actual

test_something.setup = build(
  ['__', '__/etc', ('__/etc/middleware.conf', 'random:choice')])
test_something.teardown = destroy


def test_must_be_callable():
    loader = Loader('root/__')
    try:
        loader.load_middleware()
    except StandardError, err:
        assert isinstance(err, MiddlewareConfError)

test_must_be_callable.setup = build(
  ['__', '__/etc', ('__/etc/middleware.conf', 'string:digits')])
test_must_be_callable.teardown = destroy


def test_blank_lines_skipped():
    loader = Loader('root/__')
    from random import choice
    expected = [choice, Responder]
    actual = loader.load_middleware()
    assert expected == actual

test_blank_lines_skipped.setup = build(
  ['__', '__/etc', ('__/etc/middleware.conf', '\n\nrandom:choice\n\n')])
test_blank_lines_skipped.teardown = destroy


def test_comments_ignored():
    loader = Loader('root/__')
    from random import choice, sample
    expected = [sample, choice, Responder]
    actual = loader.load_middleware()
    assert expected == actual

test_comments_ignored.setup = build(
  ['__', '__/etc', ('__/etc/middleware.conf', """
#comment
random:choice#comment
random:sample # comments
""")])
test_comments_ignored.teardown = destroy

