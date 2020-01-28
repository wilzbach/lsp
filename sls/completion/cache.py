from sls.completion.scope.current import CurrentScopeCache
from sls.completion.scope.global_ import GlobalScopeCache
from sls.logging import logger


log = logger(__name__)


class ContextCache:
    """
    Cache for other global blocks which caches global context like
        - FunctionTable
        - SymbolTable (global)
    """

    def __init__(self, hub, until_cursor_line=True):
        self.global_ = GlobalScopeCache(story_hub=hub)
        self.current = CurrentScopeCache(
            self.global_, hub=hub, until_cursor_line=until_cursor_line
        )

    def update(self, context):
        self.global_.update(context)
        self.current.update(context)

    def complete(self, word):
        """
        Complete with symbols in the current scope and global symbols.
        """
        yield from self.current.complete(word)
        yield from self.global_.complete(word)

    def function(self, fn_name):
        """
        Returns a matching function or None.
        """
        return self.global_.function(fn_name)

    def service_objects(self):
        """
        Yield all service object variables.
        """
        yield from self.current.service_objects()
