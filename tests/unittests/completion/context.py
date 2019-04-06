from sls.completion.context import CompletionContext


def test_context(magic):
    doc = magic()
    ws = 12
    pos = 42

    context = CompletionContext(ws, doc, pos)

    doc.word_on_cursor.assert_called_with(pos)
    doc.line_to_cursor.assert_called_with(pos)

    assert context.ws == ws
    assert context.doc == doc
    assert context.pos == pos
    assert context.word == doc.word_on_cursor()
    assert context.line == doc.line_to_cursor()
