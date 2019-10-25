from pytest import raises

from sls.completion.item import CompletionItem


def test_to_completion():
    item = CompletionItem()
    with raises(NotImplementedError):
        item.to_completion()


def test_completion_build():
    item = CompletionItem()
    result = item.completion_build(label='label', detail='detail',
                                   documentation='doc',
                                   completion_kind=2, context=None)
    assert result == {
        'label': 'label',
        'kind': 2,
        'detail': 'detail',
        'documentation': 'doc',
        'insertTextFormat': 1,
    }


def test_completion_build_sort_text():
    item = CompletionItem()
    result = item.completion_build(label='label', detail='detail',
                                   documentation='doc',
                                   completion_kind=2, context=None,
                                   sort_text='.sort.', filter_text='.filter.')
    assert result == {
        'label': 'label',
        'kind': 2,
        'detail': 'detail',
        'documentation': 'doc',
        'insertTextFormat': 1,
        'sortText': '.sort.',
        'filterText': '.filter.',
    }
