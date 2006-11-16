from aspen.colon import *
from aspen.tests import assert_raises as _assert_raises


def assert_raises(name, Err):
    _assert_raises(Err, colonize, name, 'filename', 0)


# Working
# =======

def test_basic():
    from aspen.handlers import HTTP404 as expected
    actual = colonize('aspen.handlers:HTTP404', 'filename', 0)
    assert expected is actual


# Errors
# ======

def test_must_have_colon():
    assert_raises('foo.bar', ColonizeBadColonsError)

def test_but_only_one_colon():
    assert_raises('foo.bar:baz:buz', ColonizeBadColonsError)

def test_module_name():
    assert_raises('foo.bar; import os; os.remove();:', ColonizeBadModuleError)

def test_module_not_there():
    assert_raises('foo.bar:baz', ColonizeImportError)

def test_object_name():
    assert_raises('string:baz; import os; os.remove();', ColonizeBadObjectError)

def test_object_not_there():
    assert_raises('string:foo', ColonizeAttributeError)

def test_nested_object_not_there():
    assert_raises('string:digits.duggems', ColonizeAttributeError)
