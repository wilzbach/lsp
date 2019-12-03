from sls.completion.item import (
    CompletionItem,
    CompletionItemKind,
)
from sls.logging import logger

log = logger(__name__)


class PropertyCompletionSymbol(CompletionItem):
    """
    A symbol completion item.
    """

    def __init__(self, word, name, prop):
        self.word = word
        self.name = name
        self.prop = prop

    def to_completion(self, context):
        """
        Returns a LSP representation.
        """
        full_text = f"{self.word}.{self.name}"
        desc = f"returns {self.prop}"
        return self.completion_build(
            label=self.name,
            text_edit=full_text,
            detail=desc,
            documentation=f"{self.name}",
            completion_kind=CompletionItemKind.Method,
            context=context,
            filter_text=full_text,
        )
