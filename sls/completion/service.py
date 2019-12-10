from sls.logging import logger

from sls.parser.stack import Stack

from sls.services.action import Action
from sls.services.argument import Argument
from sls.services.event import Event

from storyhub.sdk.service.Event import Event as HubEvent

from .service_data import ServiceVarType

log = logger(__name__)


class ServiceCompletion:
    """
    Provides completion for various service-related stack configurations.
    """

    def __init__(self, service_handler):
        self.service_handler = service_handler

    def process_suffix(self, stack, tokens, value_stack_name):
        """
        Extract a service_suffix (=service_name) and yield its actions.
        """
        name = Stack.extract(stack, value_stack_name)[0].value
        in_assignment = any(tok.text() == "=" for tok in tokens)
        yield from self._service_actions(name, in_assignment=in_assignment)

    def process_when_name(self, stack, tokens):
        """
        Extract a service_suffix (=service_name) after WHEN and yield its actions.
        """
        commands = self.process_suffix(stack, tokens, "when_service_name")
        for command in commands:
            if isinstance(command, Action):
                # only show commands with events inside when
                if Utils.has_events(command):
                    yield command
            else:
                yield command

    def _service_actions(self, service_name, in_assignment=False):
        """
        Yields all actions of a service.
        If the service name is a service (e.g. `http server`),
            its events will be yielded instead.
        If the service is from a service event output (e.g. `when srv listen as req`),
            its actions will be yielded instead.
        """
        service, ty = self.service_handler.check_service_var(service_name)
        if ty == ServiceVarType.DataVar:
            # a normal variable - no service object
            return
        elif ty == ServiceVarType.ServiceEvent:
            for event in service.events():
                yield Event(event)
            return
        elif ty == ServiceVarType.ServiceOutput:
            for event in service.actions():
                yield Action(event)
            return

        # variable is unknown -> it must be a service
        assert ty == ServiceVarType.Undefined

        commands = self.service_handler.actions(service_name)
        if in_assignment:
            # don't show service commands with events in assignments (a = <..>)
            for command in commands:
                if not Utils.has_events(command):
                    yield command
        else:
            yield from commands

    def process_command(self, stack, value_stack_name, command_name):
        """
        Extract previous tokens for service argument completion.
        """
        actions = self.process_suffix(stack, [], value_stack_name)
        service_command = Stack.extract(stack, command_name)[0].value
        yield from Utils.action_args(actions, service_command)

    def process_when_command(self, stack):
        """
        Extract previous tokens for service argument completion.
        """
        service_name = Stack.extract(stack, "when_expression")[0].value
        service_command = Stack.extract(stack, "when_action")[0].value
        _, ty = self.service_handler.check_service_var(service_name)
        if ty == ServiceVarType.Undefined:
            # variable was not declared -> must be a service with an action
            action = self.service_handler.action(service_name, service_command)
            if action is None:
                return
            for event in action.events():
                yield Event(event)
            return

        yield from self.when(
            service_name, service_command, event=None, prev_args=[]
        )

    def process_args(self, stack, prev_args):
        """
        Looks for the service name and command token in the
        Filters previously seen arguments.
        """
        service_name = Stack.extract(stack, "value", "service_suffix")[0].value
        service_command = Stack.extract(stack, "service_suffix")[0].value
        service = self._service_actions(service_name)
        args = Utils.action_args(service, service_command)
        yield from Utils.filter_prev_args(args, prev_args)

    def when(self, service_name, action, event, prev_args):
        """
        Process a when statement.
        when <service_name> <action> <event> <prev_args>
        """
        log.debug(
            "when %s action:%s event:%s (prev: %s)",
            service_name,
            action,
            event,
            prev_args,
        )
        if event is None:
            # only two names -> the first one must be a service object
            event = action
            action, ty = self.service_handler.check_service_var(service_name)
            if ty == ServiceVarType.DataVar:
                # a normal variable - no service object
                return
            elif ty == ServiceVarType.Undefined:
                # no variable -> no completion
                return
            elif ty == ServiceVarType.ServiceOutput:
                # nested whens are not allowed (for now)
                return
            assert ty == ServiceVarType.ServiceEvent
        else:
            # List all event arguments of the service.
            action = self.service_handler.action(service_name, action)
            if action is None:
                return

        args = Utils.action_args(action.events(), event)
        yield from Utils.filter_prev_args(
            args, prev_args,
        )


class Utils:
    @staticmethod
    def filter_prev_args(args, prev_args):
        """
        Filter a list of previously seen arguments from an argument iterator.
        """
        for arg in args:
            arg_name = arg.argument.name().lower()
            # ignore previously used args
            if arg_name not in prev_args:
                yield arg

    @staticmethod
    def action_args(actions, action_name):
        """
        Only yield args from an action of with name `action_name`.
        """
        for action in actions:
            if isinstance(action, Action):
                command = action.action
            else:
                assert isinstance(action, HubEvent), action
                command = action

            if command.name() == action_name:
                for arg in command.args():
                    yield Argument(arg)

    @staticmethod
    def has_events(command):
        """
        Returns `True` if a command has events attached to it.
        """
        assert isinstance(command, Action)
        return len(command.action.events()) > 0
