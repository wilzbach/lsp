import json

from pytest import fixture

from sls.services.hub import ServiceHub
import sls.services.hub as HubModule

from storyhub.sdk.AutoUpdateThread import AutoUpdateThread
from storyhub.sdk.ServiceWrapper import ServiceWrapper


@fixture
def no_updates(patch):
    patch.init(AutoUpdateThread)


@fixture
def cache_dir(patch, tmpdir):
    patch.object(HubModule, "get_cache_dir", return_value=tmpdir)
    return tmpdir


def test_hub_create_json(patch, cache_dir, no_updates):
    patch.object(ServiceWrapper, "fetch_services", return_value=[])
    hub_path = cache_dir.join("hub.json")
    hub = ServiceHub()
    assert hub.hub_path == hub_path
    assert hub_path.read() == "[]"
    AutoUpdateThread.__init__.assert_called()


def test_hub_get_existing_json(patch, cache_dir, no_updates):
    patch.object(ServiceWrapper, "fetch_services")
    patch.object(ServiceHub, "update_service_wrapper")
    service = {
        "service": {
            "name": "foo",
            "alias": None,
            "owner": {"username": "baruser"},
        }
    }
    cache_dir.join("hub.json").write(f"[{json.dumps(service)}]")
    ServiceHub()
    ServiceWrapper.fetch_services.assert_not_called()
    ServiceHub.update_service_wrapper.assert_not_called()
    AutoUpdateThread.__init__.assert_called()


def test_hub_create_dir(patch, tmpdir, no_updates):
    """
    Ensures that ServiceHub creates missing directories.
    """
    cache_dir = tmpdir.join("extra_dir")
    patch.object(HubModule, "get_cache_dir", return_value=cache_dir)
    patch.object(ServiceWrapper, "fetch_services", return_value=[])
    hub_path = cache_dir.join("hub.json")
    hub = ServiceHub()
    assert hub.hub_path == hub_path
    assert hub_path.read() == "[]"
    AutoUpdateThread.__init__.assert_called()
