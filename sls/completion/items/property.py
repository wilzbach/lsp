from sls.completion.items.item import (
    CompletionItem,
    CompletionItemKind,
    SortGroup,
)
from sls.logging import logger

from storyscript.compiler.semantics.types.Types import BaseType

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
        ty = self.prop
        if not isinstance(ty, BaseType):
            ty = ty.type()
        desc = f"returns {ty}"
        return self.completion_build(
            label=self.name,
            text_edit=full_text,
            detail=desc,
            documentation=f"{self.name}",
            completion_kind=CompletionItemKind.Method,
            context=context,
            filter_text=full_text,
            sort_group=SortGroup.Property,
        )
