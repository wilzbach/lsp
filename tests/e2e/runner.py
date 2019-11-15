#!/usr/bin/env pytest

import io
import json
from glob import glob
from os import path

from pytest import mark

from sls import App

from storyhub.sdk.ServiceWrapper import ServiceWrapper


test_dir = path.dirname(path.realpath(__file__))
# make the test_file paths relative, s.t. test paths are nice to read
test_files = list(
    map(
        lambda e: path.relpath(e, test_dir),
        glob(path.join(test_dir, "**", "*.story"), recursive=True),
    )
)

script_dir = path.dirname(path.realpath(__file__))
fixture_dir = path.join(script_dir, "..", "fixtures", "hub")
fixture_file = path.join(fixture_dir, "hub.fixed.json")

hub = ServiceWrapper.from_json_file(fixture_file)


# compile a story and compare its completion with the expected tree
def run_test_completion(uri, source, expected, patch):
    assert App(hub=hub).complete(uri=uri, text=source) == expected


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
    return run_test_completion(story_path, story_string, expected, patch)


@mark.parametrize("test_file", test_files)
def test_story(test_file, patch):
    test_file = path.join(test_dir, test_file)
    run_test(test_file, patch)
