from sls.completion.item import CompletionItem, CompletionItemKind
from sls.document import Position, Range, TextEdit

from .argument import Argument
from .event import Event


class Action(CompletionItem):
    """
    A service action that exposes events.
    """

    def __init__(self, name, description, args, events):
        self._name = name
        self._description = description
        self._args = args
        self._events = events

    @classmethod
    def from_hub(cls, name, action):
        args = {}
        if 'arguments' in action:
            for arg_name, arg in action['arguments'].items():
                args[arg_name] = Argument.from_hub(name=arg_name, argument=arg)

        events = {}
        if 'events' in action:
            for event_name, event in action['events'].items():
                events[event_name] = Event.from_hub(name=event_name,
                                                    event=event)

        if isinstance(action, str):
            description = action
        else:
            description = action.get(
                'help', 'No description available'
            )

        return cls(
            name=name,
            description=description,
            args=args,
            events=events,
        )

    def name(self):
        return self._name

    def description(self):
        return self._description

    def args(self):
        return self._args.values()

    def arg(self, name):
        return self._events.get(name, None)

    def events(self):
        return self._events.values()

    def event(self, name):
        return self._events.get(name, None)

    def to_completion(self, context):
        detail = self.description().split('\n')[0]
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
            detail=f'Action: {detail}',
            text_edit=TextEdit(Range(start, end), f'{self.name()} '),
            documentation=self.description(),
            completion_kind=CompletionItemKind.Unit,
            context=context,
        )
