from sls.completion.context import CompletionContext
from sls.completion.scope.global_ import GlobalScopeCache
from sls.document import Document, Position

from storyscript.compiler.semantics.symbols.Scope import Scope


def test_error(magic):
    doc = Document(uri=".text.", text="a = $\n  b = \n")
    pos = Position(1, 4)
    context = CompletionContext(ws=magic(), doc=doc, pos=pos)
    glob = GlobalScopeCache()
    glob.update(context)
    fns = [*glob.function_table.functions.keys()]
    assert fns == []


def test_caching(magic):
    doc = Document(uri=".text.", text="function foo\n  a = 1\n\nb = 0")
    pos = Position(3, 0)
    context = CompletionContext(ws=magic(), doc=doc, pos=pos)
    global_ = magic()
    global_.global_scope = Scope.root()
    glob = GlobalScopeCache()
    glob.update(context)
    fns = [*glob.function_table.functions.keys()]
    assert fns == ["foo"]


def test_complete(magic):
    doc = Document(uri=".text.", text="function foo\n  a = 1\n\nb = 0")
    pos = Position(3, 0)
    context = CompletionContext(ws=magic(), doc=doc, pos=pos)
    global_ = magic()
    global_.global_scope = Scope.root()
    glob = GlobalScopeCache()
    glob.update(context)
    assert [x.function.name() for x in glob.complete("f")] == ["foo"]
    assert [x.function.name() for x in glob.complete("b")] == []
