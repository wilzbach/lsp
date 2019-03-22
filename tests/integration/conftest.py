import json
from os import path

from asyncy.hub.sdk.AsyncyHub import AsyncyHub
from asyncy.hub.sdk.db.Service import Service

from playhouse.shortcuts import dict_to_model

from pytest import fixture


def singleton(fn):
    """
    Lazily instantiate a function
    """
    _instance = None

    def wrapped():
        nonlocal _instance
        if _instance is None:
            _instance = fn()
        return _instance
    return wrapped


@singleton
def load():
    script_dir = path.dirname(path.realpath(__file__))
    fixture_dir = path.join(script_dir, '..', 'fixtures', 'hub')

    services = {}
    with open(path.join(fixture_dir, 'hub.fixed.json'), 'r') as f:
        services = json.load(f)

    for k, v in services.items():
        services[k] = dict_to_model(Service, v)

    def get_service(alias=None, owner=None, name=None):
        if alias:
            return services[alias]
        else:
            return services[f'{owner}/{name}']

    def get_all_service_names():
        return services.keys()

    return get_service, get_all_service_names


@fixture
def hub(patch):
    patch.many(AsyncyHub, ['update_cache', 'get_all_service_names', 'get'])
    get_service, get_all_service_names = load()
    AsyncyHub.get.side_effect = get_service
    AsyncyHub.get_all_service_names.side_effect = get_all_service_names
