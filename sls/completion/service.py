from sls.logging import logger

from sls.parser.stack import Stack

from sls.services.action import Action
from sls.services.argument import Argument

log = logger(__name__)


class ServiceCompletion:
    def __init__(self, service_registry):
        self.service_registry = service_registry

    def process_name(self, stack):
        """
        Yields the commands of the respective service if it exists.
        """
        service_name = Stack.extract(stack, "value")[0].value
        log.debug("commands - %s", service_name)
        service = self.service_registry.get_service_data(service_name)
        if service is None:
            return

        service_config = service.configuration()
        for action in service_config.actions():
            yield Action(action)

    def process_args(self, stack, prev_args):
        """
        Looks for the service name and command token in the stack and filter seen arguments.
        """
        service_name = Stack.extract(stack, "value", "service_suffix")[0].value
        service_command = Stack.extract(stack, "service_suffix")[0].value
        args = self._args(service_name, service_command)
        for arg in args:
            arg_name = arg.argument.name().lower()
            # ignore previously used args
            if arg_name not in prev_args:
                yield arg

    def process_command(self, stack):
        """
        Extract previous tokens for service argument completion.
        """
        service_name = Stack.extract(stack, "value")[0].value
        service_command = Stack.extract(stack, "service_op")[0].value
        yield from self._args(service_name, service_command)

    def _args(self, service_name, command_name):
        """
        Yields the arguments of the respective service command if it exists.
        """
        log.debug("args - %s %s", service_name, command_name)
        service = self.service_registry.get_service_data(service_name)
        if service is None:
            return

        service_config = service.configuration()

        command = service_config.command(command_name)
        if command is not None:
            for arg in command.args():
                yield Argument(arg)

        action = service_config.action(command_name)
        if action is not None:
            for arg in action.args():
                yield Argument(arg)

    def services(self, word):
        yield from self.service_registry.find_services(word)
