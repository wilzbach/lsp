from sls.completion.item import CompletionItem, CompletionItemKind


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
        return self.completion_build(
            label=self.argument.name(),
            text_edit=f'{self.argument.name()}:',
            detail=f'Arg. {self.argument.type()}',
            documentation=self.argument.help(),
            completion_kind=CompletionItemKind.Value,
            context=context,
        )
