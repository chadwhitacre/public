import os

from aspen import load
from aspen.httpy import Responder
from aspen.tests import assert_raises
from aspen.tests.fsfix import mk, attach_rm
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


# No middleware configured
# ========================

def test_no_magic_directory():
    loader = Loader()
    loader.paths.__ = None
    expected = [Responder]
    actual = loader.load_middleware()
    assert actual == expected

def test_no_file():
    mk('__', '__/etc')
    loader = Loader()
    expected = [Responder]
    actual = loader.load_middleware()
    assert actual == expected

def test_empty_file():
    mk('__', '__/etc', ('__/etc/middleware.conf', ''))
    loader = Loader()
    expected = []
    actual = loader.load_apps()
    assert actual == expected


# Middleware configured
# =====================

def test_something():
    mk('__', '__/etc', ('__/etc/middleware.conf', 'random:choice'))
    loader = Loader()
    expected = [random.choice, Responder]
    actual = loader.load_middleware()
    assert actual == expected

def test_must_be_callable():
    mk('__', '__/etc', ('__/etc/middleware.conf', 'string:digits'))
    loader = Loader()
    err = assert_raises(MiddlewareConfError, loader.load_middleware)
    assert err.msg == "'string:digits' is not callable"


# Basics
# ======

def test_blank_lines_skipped():
    mk('__', '__/etc', ('__/etc/middleware.conf', '\n\nrandom:choice\n\n'))
    loader = Loader()
    expected = [random.choice, Responder]
    actual = loader.load_middleware()
    assert actual == expected

def test_comments_ignored():
    mk('__', '__/etc', ('__/etc/middleware.conf', """

        #comment
        random:choice#comment
        random:sample # comments

        """))
    loader = Loader()
    expected = [random.sample, random.choice, Responder]
    actual = loader.load_middleware()
    assert actual == expected


# Remove the filesystem fixture after each test.
# ==============================================

attach_rm(globals(), 'test_')