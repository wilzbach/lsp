from sls.parser.parso import Parser
from sls.parser.token import StoryTokenSpace, TokenType


def parse(text):
    parser = Parser()
    stack = parser.stack(text)
    return [*parser.transitions_tokens(stack)]


def expr():
    return [
        # StoryTokenSpace.TIME,
        # StoryTokenSpace.REGEX,
        StoryTokenSpace.STRING,
        StoryTokenSpace.NULL,
        StoryTokenSpace.NUMBER,
        StoryTokenSpace.NAME,
        StoryTokenSpace.LPARENS,
        "{",
        "[",
        "true",
        "false",
        "not",
    ]


def op():
    return [
        "/",
        "*",
        "+",
        "-",
        "%",
        "^",
        "to",
        "and",
        "or",
        "<",
        "<=",
        "==",
        "!=",
        ">",
        ">=",
        "=",
        "+=",
        "-=",
        "*=",
        "/=",
        "%=",
    ]


def comp(val):
    if isinstance(val, TokenType):
        return val.name
    return val


def compare(a, b):
    a = set(sorted(a, key=comp))
    b = set(sorted(b, key=comp))
    assert a == b


def test_parser_add_expr():
    s = parse("2 +")
    compare(s, expr())


def test_parser_add_expr_op():
    s = parse("2 ")
    compare(s, op())


def test_parser_fn():
    s = parse("foo(")
    assert s == [StoryTokenSpace.NAME]


def test_parser_fn_colon():
    s = parse("foo(a")
    assert s == [StoryTokenSpace.COLON]


def test_parser_fn_value():
    s = parse("foo(a:")
    compare(s, expr())


def test_parser_fn_end():
    s = parse("foo(a:1")
    compare(s, op() + [StoryTokenSpace.RPARENS, StoryTokenSpace.NAME])


def test_parser_service():
    s = parse("foo ")
    compare(s, op() + [StoryTokenSpace.LPARENS, StoryTokenSpace.NAME])


def test_parser_service_args():
    s = parse("foo bar")
    compare(s, op() + [StoryTokenSpace.NAME])


def test_parser_service_value():
    s = parse("foo bar a:")
    compare(s, expr())


def test_parser_service_end():
    s = parse("foo bar a:1")
    compare(s, op() + [StoryTokenSpace.NAME])


def test_parser_if_expr():
    s = parse("if")
    compare(s, expr())


def test_parser_if_block():
    s = parse("if a\n")
    compare(s, [StoryTokenSpace.INDENT])
