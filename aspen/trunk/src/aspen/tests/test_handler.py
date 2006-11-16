import StringIO

from aspen.exceptions import *
from aspen.load import Handler as _Handler
from aspen.tests import assert_raises


# Fixture
# =======

import random

def handle():
    return 'BLAM!!!'

def always_true(fp, pred):
    return True

def always_false(fp, pred):
    return False

def rule(fp, predicate):
    return predicate == 'foo'

def Handler(*rules, **rulefuncs):
    if not rulefuncs:
        rulefuncs = {'foo':always_true}
    handler = _Handler(rulefuncs, handle)
    for rule in rules:
        handler.add(*(rule,0))
    return handler

fp = StringIO.StringIO("foo")



# Basic
# =====

def test_basic():
    handler = Handler()
    assert str(handler) == '<handler handle>'
    assert handler.handle() == 'BLAM!!!'


# Add
# ===

def test_add():
    handler = Handler("foo true")
    expected = [('foo', 'true')]
    actual = handler._rules
    assert actual == expected

def test_add_two():
    handler = Handler("foo true")
    handler.add("AND foo false", 0)
    expected = [('foo', 'true'), ('and', 'foo', 'false')]
    actual = handler._rules
    assert actual == expected

def test_add_booleans(): # also tests > 2 rules, and dupes
    handler = Handler("foo true")
    handler.add("AND foo true", 0)
    handler.add("and foo true", 0)
    handler.add("OR foo true", 0)
    handler.add("or foo true", 0)
    handler.add("NOT foo true", 0)
    handler.add("not foo true", 0)
    expected = [ ('foo', 'true')
               , ('and', 'foo', 'true')
               , ('or', 'foo', 'true')
               , ('and not', 'foo', 'true')
                ]
    actual = handler._rules
    assert actual == expected

def test_add_first_rule_with_implicit_predicate():
    handler = Handler()
    handler.add("foo", 0)
    expected = [('foo', None)]
    actual = handler._rules
    assert actual == expected

def test_add_second_rule_with_implicit_predicate():
    handler = Handler("foo true")
    handler.add("AND foo", 0)
    expected = [('foo', 'true'), ('and', 'foo', None)]
    actual = handler._rules
    assert actual == expected

def test_add_first_predicate_with_whitespace():
    handler = Handler()
    handler.add("foo true is as true does", 0)
    expected = [('foo', 'true is as true does')]
    actual = handler._rules
    assert actual == expected

def test_add_second_predicate_with_whitespace():
    handler = Handler("foo true")
    handler.add("NOT foo true is as true does", 0)
    expected = [('foo', 'true'), ('and not', 'foo', 'true is as true does')]
    actual = handler._rules
    assert actual == expected


# Add Errors
# ==========

def test_add_first_not_enough_tokens():
    handler = Handler()
    err = assert_raises(HandlersConfError, handler.add, "", 0)
    assert err.msg == "need one or two tokens in ''"

def test_add_second_not_enough_tokens():
    handler = Handler("foo true")
    err = assert_raises(HandlersConfError, handler.add, "", 0)
    assert err.msg ==  "need two or three tokens in ''"
    err = assert_raises(HandlersConfError, handler.add, "foo", 0)
    assert err.msg ==  "need two or three tokens in 'foo'"

def test_add_unknown_rule():
    handler = Handler()
    err = assert_raises(HandlersConfError, handler.add, "bar true", 0)
    assert err.msg == "no rule named 'bar'"

def test_add_second_two_tokens_bad_boolean():
    handler = Handler("foo true")
    err = assert_raises(HandlersConfError, handler.add, "blah foo", 0)
    assert err.msg ==  "bad boolean 'blah' in 'blah foo'"

def test_add_second_three_tokens_bad_boolean():
    handler = Handler("foo true")
    err = assert_raises(HandlersConfError, handler.add, "blah foo bar", 0)
    assert err.msg ==  "bad boolean 'blah' in 'blah foo bar'"


# Match
# =====

def test_match():
    handler = Handler("foo true")
    assert handler.match(fp)

def test_match_false():
    handler = Handler("bar", bar=always_false)
    assert not handler.match(fp)

def test_match_two():
    handler = Handler( "foo"
                     , "NOT bar "
                     , foo = always_true
                     , bar = always_false
                      )
    assert handler.match(fp)

def test_match_three():
    handler = Handler( "foo"
                     , "NOT bar"
                     , "OR foo"
                     , foo = always_true
                     , bar = always_false
                      )
    assert handler.match(fp)

def test_match_with_predicate_true():
    handler = Handler("rule foo", rule=rule)
    assert handler.match(fp)

def test_match_with_predicate_false():
    handler = Handler("rule bar", rule=rule)
    assert not handler.match(fp)

def test_match_complex():
    handler = Handler( "foo"
                     , "NOT bar"
                     , "OR rule foo"
                     , bar=always_false
                     , foo=always_true
                     , rule=rule
                      )
    assert handler.match(fp)


# Match Errors
# ============

def test_match_no_rules():
    handler = Handler()
    err = assert_raises(HandlerError, handler.match, fp)
    assert err.msg == "no rules to match"

