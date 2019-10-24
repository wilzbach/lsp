from sls.completion.ast import ASTAnalyzer

from storyscript.parser import Parser


def test_ast(magic, patch):
    registry = magic()
    context = magic()
    patch.object(Parser, 'parse')
    patch.object(ASTAnalyzer, 'try_ast')
    context.line = 'foo'

    ast = ASTAnalyzer(service_registry=registry)
    result = [*ast.complete(context)]

    Parser.parse.assert_called_with(context.line, allow_single_quotes=False)
    ASTAnalyzer.try_ast.assert_called_with(Parser.parse(), context.word, False)

    assert result == []
