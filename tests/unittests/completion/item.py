from pytest import fixture, raises

from sls.completion.items.item import CompletionItem


@fixture
def context(magic):
    c = magic()
    c.word = ""
    c.context_word = ""
    return c


def test_to_completion():
    item = CompletionItem()
    with raises(NotImplementedError):
        item.to_completion()


def test_completion_build(context):
    item = CompletionItem()
    result = item.completion_build(
        label="label",
        detail="detail",
        documentation="doc",
        completion_kind=2,
        context=context,
        sort_group=10,
    )
    assert result == {
        "label": "label",
        "kind": 2,
        "detail": "detail",
        "documentation": "doc",
        "sortText": "10-label",
        "insertTextFormat": 1,
    }


def test_completion_build_sort_text(context):
    item = CompletionItem()
    result = item.completion_build(
        label="label",
        detail="detail",
        documentation="doc",
        completion_kind=2,
        context=context,
        sort_group=20,
    )
    assert result == {
        "label": "label",
        "kind": 2,
        "detail": "detail",
        "documentation": "doc",
        "insertTextFormat": 1,
        "sortText": "20-label",
    }
