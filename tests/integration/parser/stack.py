from pytest import raises

from sls.parser.parso import Parser
from sls.parser.stack import Stack


def test_extract():
    stack = Parser().stack("foo bar foo:1")
    res = Stack.extract(stack, "arglist", "value")
    assert len(res) == 2
    assert res[0].value == "foo"
    assert res[1].value == ":"


def test_extract_no_rule():
    stack = Parser().stack("foo bar foo:1")
    with raises(AssertionError):
        Stack.extract(stack, "no_rule")


def test_extract_seen_no_rule():
    stack = Parser().stack("foo bar foo:1")
    with raises(AssertionError):
        Stack.extract(stack, "arglist", "no_rule")


def test_stack_find_closest_rule():
    stack = Parser().stack("foo bar foo:1")
    res = Stack.find_closest_rule(stack, ["arglist", "no_rule"])
    assert res == "arglist"


def test_stack_find_closest_rule_no_rule():
    stack = Parser().stack("foo bar foo:1")
    with raises(AssertionError):
        Stack.find_closest_rule(stack, ["no_rule"])


def test_stack_find_all_until():
    stack = Parser().stack("foo bar arg1:1")
    res = Stack.find_all_until(stack, "arglist", ["service_suffix"])
    assert [*res] == ["arg1"]


def test_stack_find_all_until_2():
    stack = Parser().stack("foo bar arg1:1 + 1 arg2:2")
    res = Stack.find_all_until(stack, "arglist", ["service_suffix"])
    assert [*res] == ["arg1", "arg2"]


def test_stack_find_all_until_3():
    stack = Parser().stack("foo bar arg1:1 + 1 arg2:2 arg3: (foo bar arg4:1)")
    res = Stack.find_all_until(stack, "arglist", ["service_suffix"])
    assert [*res] == ["arg1", "arg2", "arg3"]


def test_stack_find_all_until_no_rule():
    stack = Parser().stack("foo bar foo:1")
    with raises(AssertionError):
        [*Stack.find_all_until(stack, "arglist", ["no_rule"])]
