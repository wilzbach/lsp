from storyhub.sdk.StoryscriptHub import StoryscriptHub

from sls.services.service import Service

from ..logging import logger

log = logger(__name__)


class ServiceHub:
    """
    Contains a list of all available Story hub services
    """

    def __init__(self, hub=None):
        if hub is None:
            self.hub = StoryscriptHub()
        else:
            self.hub = hub

    def find_services(self, keyword):
        for service_name in self.hub.get_all_service_names():
            if service_name.startswith(keyword):
                try:
                    service = Service(self.get_service_data(service_name))
                    service.set_name(service_name)
                    yield service
                except BaseException:
                    # ignore all invalid services
                    log.error(
                        "Service '%s' has an invalid config", service_name
                    )

    def get_service_data(self, service_name):
        return self.hub.get(alias=service_name)
