from sls.completion.item import CompletionItem, CompletionItemKind
from sls.document import Position, Range, TextEdit


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
        start = Position(
            line=context.pos.line,
            character=context.pos.char - len(context.word),
        )
        end = Position(
            line=context.pos.line,
            character=context.pos.char,
        )
        return self.completion_build(
            label=self.argument.name(),
            text_edit=TextEdit(Range(start, end), f'{self.argument.name()}:'),
            detail=f'Arg. {self.argument.type()}',
            documentation=self.argument.help(),
            completion_kind=CompletionItemKind.Value,
            context=context,
        )
