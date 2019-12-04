from glob import glob
from os import path


from storyhub.sdk.ServiceWrapper import ServiceWrapper


test_dir = path.dirname(path.dirname(path.realpath(__file__)))


def find_test_files(relative=False):
    """
    Returns all available test files.
    """
    files = glob(path.join(test_dir, "**", "*.story"), recursive=True)
    if relative:
        return list(map(lambda e: path.relpath(e, test_dir), files))
    return files


fixture_dir = path.join(test_dir, "..", "fixtures", "hub")
fixture_file = path.join(fixture_dir, "hub.fixed.json")

hub = ServiceWrapper.from_json_file(fixture_file)
