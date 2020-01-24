from pytest import fixture, mark

from sls.document import Document, Position
from sls.indent.indent import Indentation
from sls.services.hub import ServiceHub

from tests.e2e.utils.fixtures import hub

indent_unit = "  "


@fixture
def ws(magic):
    return magic()


@fixture
def indentor():
    return Indentation(service_registry=ServiceHub(hub))


@mark.parametrize(
    "story,expected",
    [
        ("http server", indent_unit),
        ("", ""),
        ("$", ""),
        ("ams $.", ""),
        ("= . ", ""),
        ("/foo/b", ""),
        ("http :", ""),
        ('http "foo"', ""),
        ("function int", indent_unit),
        ("http fetch", ""),
        ("redis get", ""),
        ("invalidService get", ""),
        ("a = 1", ""),
        ("b = [1,2,3].length()", ""),
        ("when", indent_unit),
        ("foreach", indent_unit),
        ("foreach foo", indent_unit),
        ("foreach foo as b", indent_unit),
        ("if", indent_unit),
        ("if 2 + 2", indent_unit),
        ("else", indent_unit),
        ("while", indent_unit),
        ("while [1,2,3].length() > 0", indent_unit),
        ('while (redis get: "foo")', indent_unit),
        ("try", indent_unit),
        ("catch", indent_unit),
        ("function foo", indent_unit),
        ("function foo arg1:int", indent_unit),
        ("storyscript/crontab entrypoint", ""),
        ("noService noAction", ""),
        ("http noAction", ""),
        (indent_unit + "a = 1", indent_unit),
        (indent_unit + "redis get", indent_unit),
        (indent_unit + "when", 2 * indent_unit),
        (indent_unit + "foreach", 2 * indent_unit),
        (indent_unit + "if", 2 * indent_unit),
        (indent_unit + "else", 2 * indent_unit),
        (indent_unit + "while", 2 * indent_unit),
        (indent_unit + "try", 2 * indent_unit),
        (indent_unit + "catch", 2 * indent_unit),
        ("when srv listen", indent_unit),
        ('when srv listen path:"/counter"', indent_unit),
        ('when http server listen path:"/counter"', indent_unit),
        ('when http server listen path:"/counter" as request', indent_unit),
        ("http server as srv", indent_unit),
    ],
)
def test_indent(indentor, ws, story, expected):
    doc = Document(uri=".my.uri.", text=story)
    lines = story.split("\n")
    # select the last pos in the provided story
    pos = Position(line=len(lines) - 1, character=len(lines[-1]))
    assert (
        indentor.indent(ws, doc, pos, indent_unit="  ")["indent"] == expected
    )


def test_indent_options(indentor, ws):
    doc = Document(uri=".my.uri.", text="  try")
    pos = Position(line=0, character=8)
    assert (
        indentor.indent(ws, doc, pos, indent_unit="    ")["indent"] == "      "
    )


def test_indent_edits(indentor, ws):
    doc = Document(uri=".my.uri.", text="a = 1")
    pos = Position(line=0, character=5)
    assert indentor.indent(ws, doc, pos, indent_unit="  ") == {
        "indent": "",
        "textEdits": [
            {
                "newText": "\n",
                "range": {
                    "end": {"character": 5, "line": 0},
                    "start": {"character": 5, "line": 0},
                },
            }
        ],
    }


def test_indent_edits2(indentor, ws):
    doc = Document(uri=".my.uri.", text="\ntry")
    pos = Position(line=1, character=3)
    assert indentor.indent(ws, doc, pos, indent_unit="  ") == {
        "indent": indent_unit,
        "textEdits": [
            {
                "newText": "\n" + indent_unit,
                "range": {
                    "end": {"character": 3, "line": 1},
                    "start": {"character": 3, "line": 1},
                },
            }
        ],
    }
