from pytest import fixture

from storyhub.sdk.StoryscriptHub import StoryscriptHub

from tests.e2e.utils.fixtures import hub as story_hub


@fixture
def hub(patch):
    patch.many(
        StoryscriptHub, ["update_cache", "get_all_service_names", "get"]
    )
    StoryscriptHub.get.side_effect = story_hub.get
    StoryscriptHub.get_all_service_names.side_effect = (
        story_hub.get_all_service_names
    )
    return story_hub
