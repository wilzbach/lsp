from sls.logging import logger

from .ast import ASTAnalyzer
from .context import CompletionContext


log = logger(__name__)


class Completion():
    def __init__(self, plugins):
        self.plugins = plugins

    """
    Builds a completion list
    """
    def complete(self, ws, doc, pos):
        """"
        See the LSP Protocol on Completion [1].
        [1] https://microsoft.github.io/language-server-protocol/specification#textDocument_completion
        """  # noqa
        # Initialize context
        context = CompletionContext(ws=ws, doc=doc, pos=pos)
        log.info('Word on cursor: %s', context.word)
        items = []
        for plugin in self.plugins:
            items.extend(plugin.complete(context))

        # serialize all items
        items = [item.to_completion(context) for item in items]

        return {
            # Indicates that the list it not complete.
            # Further typing should result in recomputing this list.
            'isIncomplete': False,
            'items': items,
        }

    @classmethod
    def full(cls, service_registry):
        return cls(
            plugins=[ASTAnalyzer(service_registry)]
        )
