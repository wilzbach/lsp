from sls.completion.item import CompletionItem, CompletionItemKind

from .argument import Argument


class Event(CompletionItem):
    """
    An individual service event with its arguments.
    """

    def __init__(self, name, description, args):
        self._name = name
        self._description = description
        self._args = args

    @classmethod
    def from_hub(cls, name, event):
        args = {}
        if 'arguments' in event:
            for arg_name, arg in event['arguments'].items():
                args[arg_name] = Argument.from_hub(name=arg_name, argument=arg)

        description = event.get(
            'help', 'No description available'
        )

        return cls(
            name=name,
            description=description,
            args=args,
        )

    def name(self):
        return self._name

    def args(self):
        return self._args.values()

    def arg(self, name):
        return self._args.get(name, None)

    def to_completion(self, context):
        return self.completion_build(
            label=self.name(),
            detail=f'Event {self.name()}',
            documentation=f'Event doc: {self.name()}',
            completion_kind=CompletionItemKind.Unit,
            context=context,
        )
