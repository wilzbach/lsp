from pytest import mark

from sls.completion.cache import ContextCache
from sls.completion.context import CompletionContext
from sls.document import Document, Position


def build_cache(text, line):
    doc = Document(uri='.text.', text=text)
    pos = Position(line, 0)
    context = CompletionContext(ws=None, doc=doc, pos=pos)
    cache = ContextCache()
    cache.update(context)
    return cache


@mark.parametrize('text,line, expected', [
    ('a=1\nb=1', 0, 'app: Object\nb: int\n'),
    ('a=1\nb=1', 1, 'app: Object\na: int\n'),
    ('a=1\nb=1\nc=1', 1, 'app: Object\na: int\nc: int\n'),
])
def test_root_scope(text, expected, line, magic):
    cache = build_cache(text, line=line)
    assert cache.global_scope.symbols().pretty() == expected


@mark.parametrize('text,line, expected', [
    ('function foo\n a = 1\nb=1', 0, []),
    ('function foo\n a = 1\nb=1', 2, ['foo']),
    ('function foo\n a = 1\nb=1\nfunction bar\n c = 1', 0, ['bar']),
    ('function foo\n a = 1\nb=1\nfunction bar\n c = 1', 1, ['bar']),
    ('function foo\n a = 1\nb=1\nfunction bar\n c = 1', 2, ['foo', 'bar']),
    ('function foo\n a = 1\nb=1\nfunction bar\n c = 1', 3, ['foo']),
    ('function foo\n a = 1\nb=1\nfunction bar\n c = 1', 4, ['foo']),
])
def test_fn_table(text, expected, line, magic):
    cache = build_cache(text, line=line)
    assert list(cache.function_table.functions.keys()) == expected
