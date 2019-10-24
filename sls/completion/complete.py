from sls.logging import logger

from .ast import ASTAnalyzer
from .context import CompletionContext
from .keyword import KeywordCompletion


log = logger(__name__)


class Completion():
    """
    Builds a completion list
    """

    def __init__(self, plugins):
        self.plugins = plugins

    def gather_completion(self, context):
        for plugin in self.plugins:
            ret = plugin.complete(context)
            # serialize all items
            for item in ret:
                yield item.to_completion(context)

    def complete(self, ws, doc, pos):
        """"
        See the LSP Protocol on Completion [1].
        [1] https://microsoft.github.io/language-server-protocol/specification#textDocument_completion
        """  # noqa

        # Initialize context
        context = CompletionContext(ws=ws, doc=doc, pos=pos)
        log.info('Word on cursor: %s', context.word)
        items = [*self.gather_completion(context)]

        return {
            # Indicates that the list it not complete.
            # Further typing should result in recomputing this list.
            'isIncomplete': False,
            'items': items,
        }

    @classmethod
    def full(cls, service_registry):
        return cls(
            plugins=[
                ASTAnalyzer(service_registry),
                KeywordCompletion(),
            ]
        )
