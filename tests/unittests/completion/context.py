from sls.completion.context import CompletionContext
from sls.document import Position


def test_context(magic):
    doc = magic()
    ws = 12
    pos = 42

    context = CompletionContext(ws, doc, pos)

    doc.word_to_cursor.assert_called_with(pos)
    doc.line_to_cursor.assert_called_with(pos)

    assert context.ws == ws
    assert context.doc == doc
    assert context.pos == pos
    assert context.word == doc.word_to_cursor()
    assert context.line == doc.line_to_cursor()


def test_context_is_cursor_at_end(magic):
    doc = magic()
    doc.line.return_value = "abc"
    context = CompletionContext(ws=None, doc=doc, pos=Position(0, 10))
    assert context.is_cursor_at_end()


def test_context_is_cursor_at_end2(magic):
    doc = magic()
    doc.line.return_value = "abc"
    context = CompletionContext(ws=None, doc=doc, pos=Position(0, 3))
    assert context.is_cursor_at_end()


def test_context_is_cursor_not_at_end(magic):
    doc = magic()
    doc.line.return_value = "abc"
    context = CompletionContext(ws=None, doc=doc, pos=Position(0, 2))
    assert not context.is_cursor_at_end()
