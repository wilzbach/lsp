from sls.completion.item import CompletionItem, CompletionItemKind
from sls.document import Position, Range, TextEdit


class Command(CompletionItem):
    """
    A service command completion item.
    """

    def __init__(self, command):
        self.command = command

    def to_completion(self, context):
        start = Position(
            line=context.pos.line,
            character=context.pos.char - len(context.word),
        )
        end = Position(
            line=context.pos.line,
            character=context.pos.char,
        )
        return self.completion_build(
            label=self.command.name(),
            detail=f'Command: {self.command.help()}',
            text_edit=TextEdit(Range(start, end), f'{self.command.name()} '),
            documentation=self.command.help(),
            completion_kind=CompletionItemKind.Unit,
            context=context,
        )
