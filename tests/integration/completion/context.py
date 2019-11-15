from pytest import mark

from sls.completion.context import CompletionContext, ContextBlock
from sls.document import Document, Position


def document(text):
    return Document(".fake.uri.", text)


@mark.parametrize(
    "text,expected",
    [
        ("", []),
        ("a=1\nb=1", [ContextBlock(0, 1), ContextBlock(1, 2)]),
        ("a=1\nb=1\n\n", [ContextBlock(0, 1), ContextBlock(1, 2)]),
        (
            "a=1\nb=1\n\nc=3",
            [ContextBlock(0, 1), ContextBlock(1, 2), ContextBlock(3, 4)],
        ),
        ("while true\n a = 1", [ContextBlock(0, 2)]),
        ("while true\n\n a = 1", [ContextBlock(0, 3)]),
        (
            "while true\n a = 1\n\nb=1",
            [ContextBlock(0, 3), ContextBlock(3, 4)],
        ),
        (
            "while true\n a = 1\nb=1\nc=1",
            [ContextBlock(0, 2), ContextBlock(2, 3), ContextBlock(3, 4)],
        ),
        ("while true\n while true\n  a = 1", [ContextBlock(0, 3)]),
        (
            "while true\n a = 1\nb = 1",
            [ContextBlock(0, 2), ContextBlock(2, 3)],
        ),
        (
            "while true\n a = 1\n b = 1\nc = 1",
            [ContextBlock(0, 3), ContextBlock(3, 4)],
        ),
    ],
)
def test_blocks(text, expected, magic):
    doc = document(text)
    pos = Position(0, 0)
    context = CompletionContext(ws=magic(), doc=doc, pos=pos)
    assert context.blocks == expected


@mark.parametrize(
    "text,line,expected",
    [
        ("", 0, []),
        ("while true\n a = 1", 1, ["while true", " a = 1"]),
        ("while true\n a = 1\nb=1\nc=1", 1, ["while true", " a = 1"]),
        ("while true\n a = 1\nb=1\nc=1", 2, ["b=1"]),
        (
            "while true\n while true\n  a = 1",
            2,
            ["while true", " while true", "  a = 1"],
        ),
        (
            "while true\n a = 1\n b = 1\nc = 1",
            1,
            ["while true", " a = 1", " b = 1"],
        ),
    ],
)
def test_current_block(text, line, expected, magic):
    doc = document(text)
    pos = Position(line, 0)
    context = CompletionContext(ws=magic(), doc=doc, pos=pos)
    assert context.current_block() == expected


@mark.parametrize(
    "text,line,expected",
    [
        ("a=1\nb=1", 0, [ContextBlock(1, 2)]),
        ("a=1\nb=1", 1, [ContextBlock(0, 1)]),
        ("a=1\nb=1\n\nc=3", 0, [ContextBlock(1, 2), ContextBlock(3, 4)]),
        ("a=1\nb=1\n\nc=3", 1, [ContextBlock(0, 1), ContextBlock(3, 4)]),
        (
            "a=1\nb=1\n\nc=3",
            2,
            [ContextBlock(0, 1), ContextBlock(1, 2), ContextBlock(3, 4)],
        ),
        ("a=1\nb=1\n\nc=3", 3, [ContextBlock(0, 1), ContextBlock(1, 2)]),
        ("while true\n a = 1", 1, []),
        ("while true\n a = 1\n\nb=1", 0, [ContextBlock(3, 4)]),
        (
            "while true\n a = 1\nb=1\nc=1",
            0,
            [ContextBlock(2, 3), ContextBlock(3, 4)],
        ),
        (
            "while true\n a = 1\nb=1\nc=1",
            1,
            [ContextBlock(2, 3), ContextBlock(3, 4)],
        ),
        (
            "while true\n a = 1\nb=1\nc=1",
            2,
            [ContextBlock(0, 2), ContextBlock(3, 4)],
        ),
        (
            "while true\n a = 1\nb=1\nc=1",
            3,
            [ContextBlock(0, 2), ContextBlock(2, 3)],
        ),
    ],
)
def test_other_blocks(text, expected, line, magic):
    doc = document(text)
    pos = Position(line, 0)
    context = CompletionContext(ws=magic(), doc=doc, pos=pos)
    assert [*context.other_blocks()] == expected


def test_empty(magic):
    doc = document("")
    pos = Position(0, 0)
    context = CompletionContext(ws=magic(), doc=doc, pos=pos)
    assert [*context.lines_until_current_block()] == []
