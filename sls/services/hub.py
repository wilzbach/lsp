from storyhub.sdk.StoryscriptHub import StoryscriptHub


class ServiceHub():
    """
    Contains a list of all available Story hub services
    """
    def __init__(self, hub=None):
        if hub is None:
            self.hub = StoryscriptHub()
        else:
            self.hub = hub

    def find_services(self, keyword):
        services = []
        for service in self.hub.get_all_service_names():
            if service.startswith(keyword):
                services.append(self.get_service(service))
        return services

    def get_service(self, service_name):
        if '/' in service_name:
            owner, name = service_name.split('/')
            service = self.hub.get(owner=owner, name=name, wrap_service=True)
        else:
            service = self.hub.get(alias=service_name, wrap_service=True)
        return service
