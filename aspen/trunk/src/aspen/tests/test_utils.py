from aspen import utils
from aspen.tests import assert_raises


# Fixture
# =======

def function():
    pass

class Class:
    def __call__(self):
        pass
    def call(self):
        pass


# cmp_routines
# ============

def test_cmp_routines_bound_methods():
    assert utils.cmp_routines(Class().call, Class().call)

def test_cmp_routines_unbound_methods():
    assert utils.cmp_routines(Class.call, Class.call)

def test_cmp_routines_mixed_methods(): # actually, this should probably fail
    assert utils.cmp_routines(Class().call, Class.call)

def test_cmp_routines_functions():
    assert utils.cmp_routines(function, function)

def test_cmp_routines_classes():
    assert utils.cmp_routines(Class, Class)

def test_cmp_routines_instances():
    assert utils.cmp_routines(Class(), Class())


def test_cmp_routines_mixed():
    assert not utils.cmp_routines(function, Class)

def test_cmp_routines_mixed2():
    assert not utils.cmp_routines(function, Class())

def test_cmp_routines_mixed2():
    assert not utils.cmp_routines(function, Class.call)

def test_cmp_routines_mixed2():
    assert not utils.cmp_routines(function, Class().call)

