import json

from asyncy.hub.sdk.db.Service import Service

from playhouse.shortcuts import dict_to_model


class ConstServiceHub():
    """
    A constant service hub class that allows serving a pre-defined set of
    fixed services.
    """

    def __init__(self, services):
        self.services = services

    @classmethod
    def from_json(cls, path):
        services = {}
        with open(path, 'r') as f:
            services = json.load(f)

        for k, v in services.items():
            services[k] = dict_to_model(Service, v)

        return cls(services)

    def get_all_service_names(self):
        return self.services.keys()

    def get(self, alias=None, owner=None, name=None):
        if alias:
            return self.services[alias]
        else:
            return self.services[f'{owner}/{name}']
