from sls.services.hub import ServiceHub


def test_find_services_invalid_service(magic, patch):
    hub = magic()
    srv2 = magic()
    srv2.name.return_value = "srv2"
    hub.get_all_service_names.return_value = ["arv", "srv1", "srv2", "brv"]
    patch.object(
        ServiceHub, "get_service_data", side_effect=[BaseException(), srv2]
    )
    service_hub = ServiceHub(hub)
    services = [*service_hub.find_services("srv")]
    assert ServiceHub.get_service_data.call_count == 2
    assert len(services) == 1
    assert services[0].name() == "srv2"
