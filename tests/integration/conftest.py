from os import path

from pytest import fixture

from storyhub.sdk.ServiceWrapper import ServiceWrapper
from storyhub.sdk.StoryscriptHub import StoryscriptHub


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
    fixture_file = path.join(fixture_dir, 'hub.fixed.json')

    return ServiceWrapper.from_json_file(fixture_file)


@fixture
def hub(patch):
    patch.many(StoryscriptHub,
               ['update_cache', 'get_all_service_names', 'get'])
    consthub = load()
    StoryscriptHub.get.side_effect = consthub.get
    StoryscriptHub.get_all_service_names.side_effect = \
        consthub.get_all_service_names
