from os import makedirs, path

from storyhub.sdk.AutoUpdateThread import AutoUpdateThread
from storyhub.sdk.ServiceWrapper import ServiceWrapper

import appdirs

from sls.services.service import Service

from ..logging import logger

log = logger(__name__)


def get_cache_dir():
    return appdirs.user_cache_dir("storyscript", "sls")


class ServiceHub:
    """
    Contains a list of all available Story hub services
    """

    def __init__(self, hub=None):
        if hub is None:
            cache_dir = get_cache_dir()
            self.hub_path = path.join(cache_dir, "hub.json")
            if path.exists(self.hub_path):
                self.hub = ServiceWrapper.from_json_file(self.hub_path)
            else:
                makedirs(cache_dir, exist_ok=True)
                self.hub = ServiceWrapper()
                self.update_service_wrapper()
            self.update_thread = AutoUpdateThread(
                self.update_service_wrapper, initial_update=False
            )
        else:
            self.hub = hub

    def update_service_wrapper(self):
        """
        Update the in-memory ServiceWrapper and save a snapshot into
        the cache_dir.
        """
        services = self.hub.fetch_services()
        self.hub.reload_services(services)
        self.hub.as_json_file(self.hub_path)

    def find_services(self, keyword):
        for service_name in self.hub.get_all_service_names():
            if service_name.startswith(keyword):
                try:
                    service = Service(self.get_service_data(service_name))
                    service.set_name(service_name)
                    yield service
                except BaseException:
                    # ignore all invalid services
                    log.warn(
                        "Service '%s' has an invalid config", service_name
                    )

    def get_service_data(self, service_name):
        return self.hub.get(alias=service_name)
