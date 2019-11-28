from sls.completion.ast import ASTAnalyzer
from sls.parser.parso import Parser


def test_ast(magic, patch):
    registry = magic()
    context = magic()
    patch.object(Parser, "stack_tokens")
    patch.object(Parser, "transitions")
    context.line = "foo "

    ast = ASTAnalyzer(service_registry=registry, context_cache=None)
    result = [*ast.complete(context)]

    assert Parser.stack_tokens.call_count == 1
    assert len(Parser.stack_tokens.call_args[0]) == 1
    assert len(Parser.stack_tokens.call_args[0][0]) == 1
    tok = Parser.stack_tokens.call_args[0][0][0]
    assert tok.id() == "name"
    assert tok.text() == "foo"

    assert result == []
