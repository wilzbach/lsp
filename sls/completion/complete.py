from sls.logging import logger
import sls.sentry as sentry

from .ast import ASTAnalyzer
from .cache import ContextCache
from .context import CompletionContext


log = logger(__name__)


class Completion:
    """
    Builds a completion list
    """

    def __init__(self, context_cache, plugins):
        self.context_cache = context_cache
        self.plugins = plugins

    def gather_completion(self, context):
        for plugin in self.plugins:
            ret = plugin.complete(context)
            # serialize all items
            for item in ret:
                # check whether serialization is necessary
                if isinstance(item, dict):
                    yield item
                else:
                    yield item.to_completion(context)

    def complete(self, ws, doc, pos):
        """"
        See the LSP Protocol on Completion [1].
        [1] https://microsoft.github.io/language-server-protocol/specification#textDocument_completion
        """  # noqa

        # Initialize context
        context = CompletionContext(ws=ws, doc=doc, pos=pos)
        log.info("Word on cursor: %s", context.word)

        # Update context caches
        self.context_cache.update(context)

        try:
            items = self.gather_completion(context)
            items = sorted(items, key=lambda x: x["label"])
        except BaseException as e:
            sentry.handle_exception(e)
            items = []

        return {
            # Indicates that the list it not complete.
            # Further typing should result in recomputing this list.
            "isIncomplete": False,
            "items": items,
        }

    @classmethod
    def full(cls, service_registry):
        context_cache = ContextCache()
        return cls(
            context_cache=context_cache,
            plugins=[ASTAnalyzer(service_registry, context_cache),],
        )
