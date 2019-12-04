from sls.completion.items.item import CompletionItem, CompletionItemKind


class MutationArgument(CompletionItem):
    """
    A mutation argument completion item.
    """

    def __init__(self, name, ty):
        self.name = name
        self.ty = ty

    def to_completion(self, context):
        """
        Returns a LSP representation.
        """
        ty = str(self.ty.type())
        return self.completion_build(
            label=self.name,
            text_edit=f"{self.name}:",
            detail=f"Arg. {ty}",
            documentation=f"Arg. {ty}",
            completion_kind=CompletionItemKind.Unit,
            context=context,
        )
