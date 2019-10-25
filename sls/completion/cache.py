from sls.completion.scope.current import CurrentScopeCache
from sls.completion.scope.global_ import GlobalScopeCache
from sls.logging import logger


log = logger(__name__)


class ContextCache():
    """
    Cache for other global blocks which caches global context like
        - FunctionTable
        - SymbolTable (global)
    """

    def __init__(self):
        self.global_ = GlobalScopeCache()
        self.current = CurrentScopeCache(self.global_)

    def update(self, context):
        self.global_.update(context)
        self.current.update(context)

    def complete(self, word):
        """
        Complete with symbols in the current scope and global symbols.
        """
        yield from self.current.complete(word)
        yield from self.global_.complete(word)
