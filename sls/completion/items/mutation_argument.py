from sls.completion.items.item import (
    CompletionItem,
    CompletionItemKind,
    SortGroup,
)


class MutationArgument(CompletionItem):
    """
    A mutation argument completion item.
    """

    def __init__(self, name, sym):
        self.name = name
        self.sym = sym

    def to_completion(self, context):
        """
        Returns a LSP representation.
        """
        ty = str(self.sym.type())
        desc = f"[{ty}] {self.sym.desc()}"
        return self.completion_build(
            label=self.name,
            text_edit=f"{self.name}:",
            detail=desc,
            documentation="",
            completion_kind=CompletionItemKind.Unit,
            context=context,
            sort_group=SortGroup.Argument,
        )
