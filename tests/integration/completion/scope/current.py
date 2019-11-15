from sls.completion.context import CompletionContext
from sls.completion.scope.current import CurrentScopeCache
from sls.document import Document, Position

from storyscript.compiler.semantics.symbols.Scope import Scope


def test_error(magic):
    doc = Document(uri=".text.", text="a = $\n  b = \n")
    pos = Position(1, 4)
    context = CompletionContext(ws=magic(), doc=doc, pos=pos)
    global_ = magic()
    current = CurrentScopeCache(global_=global_)
    current.update(context)
    symbols = [s.name() for s in current.current_scope.symbols()]
    assert symbols == []


def test_caching(magic):
    doc = Document(uri=".text.", text="a = $")
    pos = Position(0, 0)
    context = CompletionContext(ws=magic(), doc=doc, pos=pos)
    global_ = magic()
    global_.global_scope = Scope.root()
    current = CurrentScopeCache(global_=global_)
    current.update(context)
    symbols = [s.name() for s in current.current_scope.symbols()]
    assert symbols == ["app"]

    # test caching
    current.update(context)
    symbols = [s.name() for s in current.current_scope.symbols()]
    assert symbols == ["app"]
