from sls.completion.items.item import CompletionItem
from sls.spec import CompletionItemKind


class CompletionSymbol(CompletionItem):
    """
    A symbol completion item.
    """

    def __init__(self, symbol):
        self.symbol = symbol

    def to_completion(self, context):
        """
        Returns a LSP representation.
        """
        return self.completion_build(
            label=self.symbol.name(),
            text_edit=f"{self.symbol.name()}",
            detail=f"Symbol. {self.symbol.type()}",
            documentation="TBD",
            completion_kind=CompletionItemKind.Variable,
            context=context,
        )
