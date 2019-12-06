from sls.completion.items.item import CompletionItem, SortGroup
from sls.spec import CompletionItemKind, InsertTextFormat


class CompletionFunction(CompletionItem):
    """
    A function completion item.
    """

    def __init__(self, function):
        self.function = function
        self.desc = function.pretty().replace("`", "")

    def to_completion(self, context):
        """
        Returns a LSP representation.
        """
        name = self.function.name()
        return self.completion_build(
            label=name,
            text_edit=f"{name}($1)",
            detail=self.desc,
            documentation=f"Function: {self.function.pretty()}",
            completion_kind=CompletionItemKind.Function,
            insert_text_format=InsertTextFormat.Snippet,
            context=context,
            sort_group=SortGroup.Function,
        )
