from sls.completion.item import CompletionItem, CompletionItemKind
from sls.logging import logger

log = logger(__name__)


class KeywordCompletionSymbol(CompletionItem):
    """
    A symbol completion item.
    """

    def __init__(self, keyword):
        self.keyword = keyword

    def to_completion(self, context):
        """
        Returns a LSP representation.
        """
        return self.completion_build(
            label=self.keyword,
            text_edit=f"{self.keyword} ",
            detail=self.keyword,
            documentation="TBD",
            completion_kind=CompletionItemKind.Keyword,
            context=context,
        )
