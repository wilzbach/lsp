from enum import Enum

from sls.logging import logger
from sls.services.action import Action

from storyhub.sdk.service.ServiceOutput import ServiceOutput


from .types import Types


log = logger(__name__)


class ServiceVarType(Enum):
    Undefined = 1
    DataVar = 2
    ServiceOutput = 3
    ServiceEvent = 4


class ServiceHandler:
    """
    Handles various requests about service properties.
    """

    def __init__(self, service_registry, context_cache):
        self.service_registry = service_registry
        self.context_cache = context_cache

    def services(self, word):
        """
        Yields all services starting with `word`.
        """
        yield from self.service_registry.find_services(word)

    def actions(self, service_name):
        """
        Yields the actions of the respective service if it exists.
        """
        log.debug("service: %s", service_name)
        service = self.service_registry.get_service_data(service_name)
        if service is None:
            return

        service_config = service.configuration()
        for action in service_config.actions():
            yield Action(action)

    def action(self, service_name, action_name):
        """
        Yields the specific `action_name` from a `service_name` or `None`.
        """
        log.debug("service: %s, action: %s", service_name, action_name)
        service = self.service_registry.get_service_data(service_name)
        if service is None:
            return None
        service_config = service.configuration()
        action = service_config.action(action_name)
        if action is not None:
            return action

    def check_service_var(self, name):
        """
        Resolves a variable and its type in the current context.
        It might be a:
            - DataVar (e.g. 2 or [1, 2, 3])
            - ServiceOutput (e.g. `http server`)
            - ServiceEvent (e.g. `when server listen ... as req`)
            - Undefined (var was not declared)
        """
        service_objects = (
            w.symbol.type()
            for w in self.context_cache.complete(name)
            if w.symbol.name() == name
        )
        service_object = next(service_objects, None)
        if service_object is None:
            return None, ServiceVarType.Undefined
        service = Types.service_object(service_object)
        if service is None:
            return None, ServiceVarType.DataVar
        if isinstance(service, ServiceOutput):
            # when ... as req
            return service, ServiceVarType.ServiceOutput
        # x = http server
        return service, ServiceVarType.ServiceEvent
