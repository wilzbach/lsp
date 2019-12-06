from sls.completion.items.item import (
    CompletionItem,
    CompletionItemKind,
    SortGroup,
)


class FunctionArgument(CompletionItem):
    """
    A function argument completion item.
    """

    def __init__(self, name, ty):
        self.name = name
        self.ty = ty

    def to_completion(self, context):
        """
        Returns a LSP representation.
        """
        ty = str(self.ty)
        return self.completion_build(
            label=self.name,
            text_edit=f"{self.name}:",
            detail=f"Arg. {ty}",
            documentation=f"Arg. {ty}",
            completion_kind=CompletionItemKind.Unit,
            context=context,
            sort_group=SortGroup.Argument,
        )
