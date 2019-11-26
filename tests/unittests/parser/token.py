from sls.parser.token import Token


def test_dedent_str():
    tok = Token("dedent", "", 0, 0)
    assert str(tok) == "tok(dedent)"
    assert str(tok.to_parso().type) == "TokenType(DEDENT)"


def test_indent_str():
    tok = Token("indent", "", 0, 0)
    assert str(tok) == "tok(indent)"
    assert str(tok.to_parso().type) == "TokenType(INDENT)"
