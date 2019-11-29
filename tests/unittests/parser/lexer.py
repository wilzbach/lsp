from pytest import mark, raises

from sls.parser.lexer import ErrorCodes, LexerException, Tokenizer


def tokenize(text):
    """Returns a list of tokens"""
    return [*Tokenizer(text).tokenize()]


def simple_tokenize(text):
    """Return a list of only the token ids"""
    toks = tokenize(text)
    return [k.id() for k in toks]


def test_regex_token():
    toks = tokenize("/foo/")
    assert len(toks) == 1
    assert toks[0].id() == "regex"
    assert toks[0].text() == "/foo/"


def test_regex_token_ws():
    toks = tokenize("/foo/ ")
    assert len(toks) == 1
    assert toks[0].id() == "regex"
    assert toks[0].text() == "/foo/"


def test_regex_token_flag():
    toks = tokenize("/foo/i")
    assert len(toks) == 1
    assert toks[0].id() == "regex"
    assert toks[0].text() == "/foo/i"


def test_regex_token_Div():
    toks = tokenize("/fo")
    assert len(toks) == 2
    assert toks[0].id() == "div"
    assert toks[0].text() == "/"
    assert toks[1].id() == "name"
    assert toks[1].text() == "fo"


def test_string_token():
    toks = tokenize('"a"')
    assert len(toks) == 1
    assert toks[0].id() == "string"
    assert toks[0].text() == "a"


def test_string_token_ws():
    toks = tokenize('"a" ')
    assert len(toks) == 1
    assert toks[0].id() == "string"
    assert toks[0].text() == "a"


def test_string_token_escaped():
    toks = tokenize(r'"a\\b"')
    assert len(toks) == 1
    assert toks[0].id() == "string"
    assert toks[0].text() == "a\\b"


def test_string_token_escaped_2():
    toks = tokenize(r'"a\"b"')
    assert len(toks) == 1
    assert toks[0].id() == "string"
    assert toks[0].text() == 'a"b'


def test_int_token():
    toks = tokenize("123")
    assert len(toks) == 1
    assert toks[0].id() == "int"
    assert toks[0].text() == "123"


def test_int_token_ws():
    toks = tokenize("123 ")
    assert len(toks) == 1
    assert toks[0].id() == "int"
    assert toks[0].text() == "123"


def test_int_parents():
    toks = tokenize("123)")
    assert len(toks) == 2
    assert toks[0].id() == "int"
    assert toks[1].id() == "rparens"


def test_int_op():
    toks = tokenize("1-2")
    assert len(toks) == 3
    assert toks[0].id() == "int"
    assert toks[1].id() == "sub"
    assert toks[0].id() == "int"


def test_float_token():
    toks = tokenize("123.")
    assert len(toks) == 1
    assert toks[0].id() == "float"
    assert toks[0].text() == "123."


def test_float_token_ws():
    toks = tokenize("123. ")
    assert len(toks) == 1
    assert toks[0].id() == "float"
    assert toks[0].text() == "123."


def test_name_token():
    toks = tokenize("abc")
    assert len(toks) == 1
    assert toks[0].id() == "name"
    assert toks[0].text() == "abc"


def test_name_token_op():
    toks = tokenize("abc+2")
    assert len(toks) == 3
    assert toks[0].id() == "name"
    assert toks[1].id() == "add"
    assert toks[2].id() == "int"


def test_name_token_2():
    toks = tokenize("my/serv123_ice")
    assert len(toks) == 1
    assert toks[0].id() == "name"
    assert toks[0].text() == "my/serv123_ice"


def test_name_token_3():
    toks = tokenize("omg-services/uuid")
    assert len(toks) == 1
    assert toks[0].id() == "name"
    assert toks[0].text() == "omg-services/uuid"


def test_name_token_4():
    toks = tokenize("name)")
    assert len(toks) == 2
    assert toks[0].id() == "name"
    assert toks[1].id() == "rparens"


def test_name_token_5():
    toks = tokenize("name(i")
    assert len(toks) == 3
    assert toks[0].id() == "name"
    assert toks[1].id() == "lparens"
    assert toks[2].id() == "name"


def test_name_token_ws():
    toks = tokenize("abc ")
    assert len(toks) == 1
    assert toks[0].id() == "name"
    assert toks[0].text() == "abc"


def test_newline_token():
    toks = tokenize("\n")
    assert len(toks) == 1
    assert toks[0].id() == "nl"
    assert toks[0].text() == "\n"


def test_newline_token_ws():
    toks = tokenize("\n ")
    assert len(toks) == 3
    assert toks[0].id() == "nl"
    assert toks[0].text() == "\n"
    assert toks[1].id() == "indent"
    assert toks[1].text() == " "
    assert toks[2].id() == "dedent"
    assert toks[2].text() == ""


def test_newline_token_indent():
    toks = tokenize("\n  ab")
    assert len(toks) == 4
    assert toks[0].id() == "nl"
    assert toks[0].text() == "\n"
    assert toks[1].id() == "indent"
    assert toks[1].text() == "  "
    assert toks[2].id() == "name"
    assert toks[2].text() == "ab"
    assert toks[3].id() == "dedent"
    assert toks[3].text() == ""


def test_fn_token():
    toks = tokenize("foo(")
    assert len(toks) == 2
    assert toks[0].id() == "name"
    assert toks[1].id() == "lparens"


@mark.parametrize(
    "op,id",
    [
        ("+", "add"),
        ("-", "sub"),
        ("*", "mul"),
        ("/", "div"),
        ("%", "mod"),
        ("^", "pow"),
        (".", "dot"),
        (":", "colon"),
        ("=", "assign"),
        ("(", "lparens"),
        (")", "rparens"),
        ("[", "lbracket"),
        ("]", "rbracket"),
        ("{", "lcurly"),
        ("}", "rcurly"),
        (",", "comma"),
        ("+=", "assign_add"),
        ("-=", "assign_sub"),
        ("*=", "assign_mul"),
        ("/=", "assign_div"),
        ("%=", "assign_mod"),
        ("==", "equal"),
        ("!=", "not_equal"),
        ("<=", "less_equal"),
        (">=", "greater_equal"),
        ("<", "less"),
        (">", "greater"),
        ("as", "as_operator"),
        ("to", "to_operator"),
        ("and", "and_operator"),
        ("or", "or_operator"),
        ("not", "not_operator"),
        ("return", "return"),
        ("returns", "returns"),
        ("when", "when"),
        ("foreach", "foreach"),
        ("while", "while"),
        ("function", "function"),
        ("int", "int_type"),
        ("float", "float_type"),
        ("boolean", "boolean_type"),
        ("string", "string_type"),
        ("time", "time_type"),
        ("regex", "regex_type"),
        ("object", "object_type"),
        ("any", "any_type"),
        ("Map", "map_type"),
        ("List", "list_type"),
    ],
)
def test_operator(op, id):
    toks = tokenize(op)
    assert len(toks) == 1
    assert toks[0].id() == id
    assert toks[0].text() == op

    # op with whitespace
    toks = tokenize(f"{op} ")
    assert len(toks) == 1
    assert toks[0].id() == id
    assert toks[0].text() == op


@mark.parametrize(
    "story,ids",
    [
        (
            """function foo returns object
    return app

b = foo()
""",
            [
                "function",
                "name",
                "returns",
                "object_type",
                "nl",
                "indent",
                "return",
                "name",
                "nl",
                "dedent",
                "nl",
                "name",
                "assign",
                "name",
                "lparens",
                "rparens",
                "nl",
            ],
        ),
        (
            "if 1\n  return 2\nelse\n  return 3",
            [
                "if",
                "int",
                "nl",
                "indent",
                "return",
                "int",
                "nl",
                "dedent",
                "else",
                "nl",
                "indent",
                "return",
                "int",
                "dedent",
            ],
        ),
        (
            "if 1\n  a = 1\n  return 2",
            [
                "if",
                "int",
                "nl",
                "indent",
                "name",
                "assign",
                "int",
                "nl",
                "return",
                "int",
                "dedent",
            ],
        ),
        (
            "a = 2.5 + -3.5",
            ["name", "assign", "float", "add", "sub", "float",],
        ),
        ("true*false", ["true", "mul", "false",],),
        (
            "redis set name: (mongodb findOne)",
            [
                "name",
                "name",
                "name",
                "colon",
                "lparens",
                "name",
                "name",
                "rparens",
            ],
        ),
        (
            "if true\n"
            "  if true\n"
            "    a = 1\n"
            "  else\n"
            '    a = "s"\n'
            "else\n"
            "  a = 1.5\n",
            [
                "if",
                "true",
                "nl",
                "indent",
                "if",
                "true",
                "nl",
                "indent",
                "name",
                "assign",
                "int",
                "nl",
                "dedent",
                "else",
                "nl",
                "indent",
                "name",
                "assign",
                "string",
                "nl",
                "dedent",
                "dedent",
                "else",
                "nl",
                "indent",
                "name",
                "assign",
                "float",
                "nl",
                "dedent",
            ],
        ),
    ],
)
def test_stories(story, ids):
    toks = simple_tokenize(story)
    assert toks == ids


@mark.parametrize(
    "story,error",
    [
        ('"a', ErrorCodes.string_no_end),
        ('"a\n 2', ErrorCodes.string_no_end),
        ("2a", ErrorCodes.number_only_digits),
        ("a$", ErrorCodes.name_only_alphanumeric),
        ("/rr/z", ErrorCodes.regex_invalid_flag),
        ("/rr\n", ErrorCodes.regex_no_end),
    ],
)
def test_lexer_exception(story, error):
    with raises(LexerException) as e:
        tokenize(story)

    e.value.code == error
