from sls.completion.item import CompletionItem, CompletionItemKind
from sls.document import Position, Range, TextEdit

from .argument import Argument


class Command(CompletionItem):
    """
    A service command that accepts arguments.
    """

    def __init__(self, name, description, args):
        self._name = name
        self._description = description
        self._args = args

    @classmethod
    def from_hub(cls, name, command):
        args = {}
        if 'arguments' in command:
            for arg_name, arg in command['arguments'].items():
                args[arg_name] = Argument.from_hub(name=arg_name,
                                                   argument=arg)

        description = command.get(
            'help', 'No description available'
        )
        return cls(
            name=name,
            description=description,
            args=args,
        )

    def name(self):
        return self._name

    def description(self):
        return self._description

    def args(self):
        return self._args.values()

    def arg(self, name):
        return self._args.get(name, None)

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
            label=self.name(),
            detail=f'Command: {self.description()}',
            text_edit=TextEdit(Range(start, end), f'{self.name()} '),
            documentation=self.description(),
            completion_kind=CompletionItemKind.Unit,
            context=context,
        )
