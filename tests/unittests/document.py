from pytest import mark

from sls.document import Document, Position


@mark.parametrize('text,expected', [
    ('foo\nbar', [
        'foo',
        'bar',
    ]),
    ('foo\n\nbar', [
        'foo',
        '',
        'bar',
    ]),
    (' \nfoo  .\n.\nbar', [
        ' ',
        'foo  .',
        '.',
        'bar',
    ]),
])
def test_document_line_split(text, expected, patch):
    doc = Document('fake.uri', text)
    assert doc._lines == expected
    # check public API
    assert [doc.line(i) for i in range(len(expected))] == expected


@mark.parametrize('text,pos,expected', [
    ('foo bar', (0, 0), ''),
    ('foo bar', (0, 1), 'f'),
    ('foo bar', (0, 2), 'fo'),
    ('foo bar', (0, 3), 'foo'),
    ('foo bar', (0, 4), ''),
    ('foo bar', (0, 6), 'ba'),
    ('foo bar', (0, 7), 'bar'),
    ('foo bar', (0, 8), 'bar'),  # test invalid requests
])
def test_document_word_on_cursor(text, pos, expected, patch):
    """
    Tests whether the word on the cursor is properly detected
    """
    patch.init(Document)
    patch.object(Document, 'line', return_value=text)
    doc = Document()
    r = doc.word_on_cursor(Position(*pos))
    assert r == expected
