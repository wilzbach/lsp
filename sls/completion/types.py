from storyhub.sdk.service.Action import Action

from storyscript.compiler.semantics.types.Types import ObjectType
from storyhub.sdk.service.ServiceOutput import ServiceOutput


class Types:
    """
    Storyscript type utilities.
    """

    @staticmethod
    def service_object(ty):
        if isinstance(ty, ObjectType):
            action = ty.action()
            if isinstance(action, Action):
                return action
            else:
                assert isinstance(action, ServiceOutput)
                return action
