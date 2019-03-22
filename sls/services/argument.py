from sls.completion.item import CompletionItem, CompletionItemKind
from sls.document import Position, Range, TextEdit


class Argument(CompletionItem):
    """
    A service argument.
    """

    def __init__(self, name, description, type_):
        self._name = name
        self._description = description
        self._type = type_

    @classmethod
    def from_hub(cls, name, argument):
        description = argument.get(
            'help', '.not.available'
        )
        return cls(
            name=name,
            description=description,
            type_=argument['type'],
        )

    def name(self):
        return self._name

    def description(self):
        return self._description

    def type_(self):
        return self._type

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
            label=self.name(),
            text_edit=TextEdit(Range(start, end), f'{self.name()}:'),
            detail=f'Arg. {self.type_()}',
            documentation=self.description(),
            completion_kind=CompletionItemKind.Value,
            context=context,
        )
