from pytest import raises

from sls.completion.items.item import CompletionItem


def test_to_completion():
    item = CompletionItem()
    with raises(NotImplementedError):
        item.to_completion()


def test_completion_build():
    item = CompletionItem()
    result = item.completion_build(
        label="label",
        detail="detail",
        documentation="doc",
        completion_kind=2,
        context=None,
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


def test_completion_build_sort_text():
    item = CompletionItem()
    result = item.completion_build(
        label="label",
        detail="detail",
        documentation="doc",
        completion_kind=2,
        context=None,
        sort_group=20,
        filter_text=".filter.",
    )
    assert result == {
        "label": "label",
        "kind": 2,
        "detail": "detail",
        "documentation": "doc",
        "insertTextFormat": 1,
        "sortText": "20-label",
        "filterText": ".filter.",
    }
