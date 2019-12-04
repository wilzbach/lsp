from sls.logging import logger

from sls.services.action import Action
from sls.services.argument import Argument

log = logger(__name__)


class ServiceCompletion:
    def __init__(self, service_registry):
        self.service_registry = service_registry

    def get_service_commands(self, service_name):
        """
        Yields the commands of the respective service if it exists.
        """
        log.debug("commands - %s", service_name)
        service = self.service_registry.get_service_data(service_name)
        if service is None:
            return

        service_config = service.configuration()
        for action in service_config.actions():
            yield Action(action)

    def get_service_arguments(self, service_name, command_name):
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
