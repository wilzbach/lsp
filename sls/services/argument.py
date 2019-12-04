from sls.completion.items.item import CompletionItem, CompletionItemKind

from .types import TypeMappings


class Argument(CompletionItem):
    """
    A service argument completion item.
    """

    def __init__(self, argument):
        self.argument = argument

    def to_completion(self, context):
        """
        Returns a LSP representation.
        """
        ty = TypeMappings.get_type_string(self.argument.type())
        return self.completion_build(
            label=self.argument.name(),
            text_edit=f"{self.argument.name()}:",
            detail=f"Arg. {ty}",
            documentation=self.argument.help(),
            completion_kind=CompletionItemKind.Value,
            context=context,
        )
