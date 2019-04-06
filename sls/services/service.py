from sls.completion.item import CompletionItem
from sls.document import Position, Range, TextEdit
from sls.spec import CompletionItemKind, MarkupKind

from .action import Action
from .command import Command


class Service(CompletionItem):
    """
    An individual service
    """
    def __init__(self, name, description, actions, commands, readme):
        self._name = name
        self._description = description
        self._actions = actions
        self._commands = commands
        self._readme = readme

    @classmethod
    def from_hub(cls, service_name, model):
        actions = {}
        if 'actions' in model.configuration:
            for name, action in model.configuration['actions'].items():
                actions[name] = Action.from_hub(name, action)

        commands = {}
        if 'commands' in model.configuration:
            for name, action in model.configuration['commands'].items():
                commands[name] = Command.from_hub(name, action)

        return cls(
            name=service_name,
            description=model.description,
            actions=actions,
            commands=commands,
            readme=model.readme,
        )

    def name(self):
        return self._name

    def description(self):
        return self._description

    def actions(self):
        return self._actions.values()

    def action(self, action):
        return self._actions.get(action, None)

    def commands(self):
        return self._commands.values()

    def command(self, command):
        return self._commands.get(command, None)

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
            detail=self.description(),
            text_edit=TextEdit(Range(start, end), f'{self.name()} '),
            documentation=self._readme,
            documentation_kind=MarkupKind.Markdown,
            completion_kind=CompletionItemKind.Method,
            context=context,
        )
