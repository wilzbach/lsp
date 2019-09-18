from storyhub.sdk.ServiceWrapper import ServiceWrapper


class ConstServiceHub():
    """
    A constant service hub class that allows serving a pre-defined set of
    fixed services.
    """

    def __init__(self, services):
        self.services = services

    @classmethod
    def from_json(cls, path):
        return cls(ServiceWrapper.from_json_file(path))

    @classmethod
    def update_hub_fixtures(cls, services, path):
        services = ServiceWrapper(services)
        services.as_json_file(path)

    def get_all_service_names(self):
        return self.services.get_all_service_names()

    def get(self, alias=None, owner=None, name=None, **kwargs):
        return self.services.get(alias, owner, name)
