from aspen.load import Mixin as Config
from aspen.tests.fsfix import mk, attach_rm
from aspen.website import Website as _Website


# Fixture
# =======

import random

class Foo:
    pass

def Website():
    config = Config()
    config.paths = Foo()
    config.paths.root = 'fsfix'
    config.paths.__ = 'fsfix/__'
    config.apps = config.load_apps()
    return _Website(config)


# Working
# =======

def test_get_app():
    mk('__', '__/etc', ('__/etc/apps.conf', '/ random:choice'))
    website = Website()
    expected = random.choice
    actual = website.get_app({'PATH_INFO':'/'})
    assert actual == expected, actual

def test_get_app_no_app():
    website = Website()
    expected = None
    actual = website.get_app({'PATH_INFO':'/'})
    assert actual == expected, actual

def test_get_app_doc_example():
    mk('__', '__/etc', ('__/etc/apps.conf', """

        /foo        random:choice   # will get both /foo and /foo/
        /bar/       random:sample   # /bar will redirect to /bar/
        /baz        random:shuffle  # will never be called
        /bar/baz    random:seed     # but this may be

        """))
    website = Website()
    expected = random.choice
    actual = website.get_app({'PATH_INFO':'/'})
    assert actual == expected, actual



# Errors
# ======




# Remove the filesystem fixture after each test.
# ==============================================

attach_rm(globals(), 'test_')