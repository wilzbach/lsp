from sls.completion.item import CompletionItem, CompletionItemKind
from sls.document import Position, Range, TextEdit


class Action(CompletionItem):
    """
    A service action completion item.
    """

    def __init__(self, action):
        self.action = action

    def to_completion(self, context):
        detail = self.action.help().split('\n')[0]
        start = Position(
            line=context.pos.line,
            character=context.pos.char - len(context.word),
        )
        end = Position(
            line=context.pos.line,
            character=context.pos.char,
        )
        return self.completion_build(
            label=self.action.name(),
            detail=f'Action: {detail}',
            text_edit=TextEdit(Range(start, end), f'{self.action.name()} '),
            documentation=self.action.help(),
            completion_kind=CompletionItemKind.Unit,
            context=context,
        )
