from sls.completion.complete import Completion
from sls.completion.context import CompletionContext
from sls.document import Document


def test_complete(magic, patch):
    patch.init(Document)
    patch.many(Document, ["line_to_cursor", "word_on_cursor"])
    patch.many(CompletionContext, ["_blocks"])
    cache = magic()
    c = Completion(plugins=[], context_cache=cache)
    doc = Document()
    ws = magic()
    pos = magic()
    result = c.complete(ws, doc, pos)
    assert isinstance(cache.update.call_args[0][0], CompletionContext)
    assert result == {
        "isIncomplete": False,
        "items": [],
    }


def test_complete_plugin(magic, patch):
    patch.init(Document)
    patch.many(Document, ["line_to_cursor", "word_on_cursor"])
    patch.many(CompletionContext, ["_blocks"])
    my_plugin = magic()
    i1 = magic()
    i2 = magic()
    cache = magic()
    my_plugin.complete.return_value = [i1, i2]
    c = Completion(plugins=[my_plugin], context_cache=cache)
    doc = Document()
    ws = magic()
    pos = magic()
    result = c.complete(ws, doc, pos)
    assert isinstance(my_plugin.complete.call_args[0][0], CompletionContext)
    assert result == {
        "isIncomplete": False,
        "items": [i1.to_completion(), i2.to_completion()],
    }
