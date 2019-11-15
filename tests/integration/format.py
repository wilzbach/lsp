from pytest import fixture

from sls.document import Document
from sls.format import Formatter


@fixture
def ws(magic):
    return magic()


@fixture
def formatter():
    return Formatter()


def test_format_single(formatter, ws):
    doc = Document(uri=".my.uri.", text="a=1")
    assert formatter.format(ws, doc) == [
        {
            "range": {
                "start": {"line": 0, "character": 0},
                "end": {"line": 0, "character": 3},
            },
            "newText": "a = 1",
        }
    ]


def test_format_multiple(formatter, ws):
    doc = Document(uri=".my.uri.", text="a=1\nb=2")
    assert formatter.format(ws, doc) == [
        {
            "range": {
                "start": {"line": 0, "character": 0},
                "end": {"line": 1, "character": 3},
            },
            "newText": "a = 1\nb = 2",
        }
    ]
