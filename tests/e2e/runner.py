#!/usr/bin/env pytest
import io
import json
from os import path

from pytest import fixture, mark

from sls import App

import storyscript.hub.Hub as StoryHub
from storyhub.sdk.AutoUpdateThread import AutoUpdateThread


from tests.e2e.utils.features import parse_options
from tests.e2e.utils.fixtures import find_test_files, hub, test_dir


test_files = find_test_files(relative=True)


@fixture
def patched_storyhub(mocker, scope="module"):
    mocker.patch.object(StoryHub, "StoryscriptHub", return_value=hub)
    mocker.patch.object(AutoUpdateThread, "dispatch_update")


# compile a story and compare its completion with the expected tree
def run_test_completion(uri, source, expected, patch, options):
    action = options.pop("action", "complete")
    if action == "complete":
        result = App(hub=hub).complete(uri=uri, text=source, **options)
    else:
        assert action == "click"
        result = App(hub=hub).click(uri=uri, text=source, **options)
    assert result == expected


# load a story from the file system and load its expected result file (.json)
def run_test(story_path, patch):
    story_string = None
    with io.open(story_path, "r") as f:
        story_string = f.read()

    expected_path = path.splitext(story_path)[0]
    assert path.isfile(
        expected_path + ".json"
    ), f"Path: `{expected_path}.json` does not exist."

    expected_completion = None
    with io.open(expected_path + ".json", "r") as f:
        expected_completion = f.read()

    # deserialize the expected completion
    expected = json.loads(expected_completion)

    options = parse_options(story_string)

    return run_test_completion(
        story_path, story_string, expected, patch, options
    )


@mark.usefixtures("patched_storyhub")
@mark.parametrize("test_file", test_files)
def test_story(test_file, patch):
    test_file = path.join(test_dir, test_file)
    run_test(test_file, patch)
