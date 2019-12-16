from storyscript.compiler.semantics.types.Types import ObjectType

from storyhub.sdk.service.Action import Action
from storyhub.sdk.service.ServiceOutput import ServiceOutput


class Types:
    """
    Storyscript type utilities.
    """

    @staticmethod
    def service_object(ty):
        """
        Returns the underlying action for a Storyscript service object.
        If the type is no service object or has no action,
        `None` will be returned.
        """
        if isinstance(ty, ObjectType):
            action = ty.action()
            if isinstance(action, Action):
                return action
            else:
                assert isinstance(action, ServiceOutput)
                return action

    @staticmethod
    def is_service_output(ty):
        """
        Returns `True` if the type is an service output object (e.g. `http server`)
        If the type is no service output object, `False` will be returned.
        """
        if isinstance(ty, ObjectType):
            if isinstance(ty.action(), Action):
                return True
        return False
