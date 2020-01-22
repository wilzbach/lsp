from sls.completion.items.item import (
    CompletionItem,
    CompletionItemKind,
    SortGroup,
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
        ty = self.prop.type()
        desc = f"[{ty}]"
        prop_desc = self.prop.desc()
        assert prop_desc is not None
        desc += f" {prop_desc}"
        return self.completion_build(
            label=self.name,
            text_edit=self.name,
            detail=desc,
            documentation=f"{self.name}",
            completion_kind=CompletionItemKind.Method,
            context=context,
            sort_group=SortGroup.Property,
        )
