from sls.diagnostics import Diagnostics
from sls.document import Document
from sls.spec import DiagnosticSeverity

from storyscript.Api import Api
from storyscript.Story import Story
from storyscript.exceptions import StoryError


def test_to_error(magic):
    e = magic()

    class FakeError:
        column = 10

    e.int_line.return_value = 0
    e.error = FakeError()
    d = Diagnostics(endpoint=None)
    assert d.to_error(e) == {
        'range': {
            'start': {'line': 0, 'character': 10},
            'end': {'line': 0, 'character': 11},
        },
        'message': e.short_message(),
        'severity': DiagnosticSeverity.Error
    }


def test_to_error_end(magic):
    e = magic()
    e.int_line.return_value = 0
    e.error.column = 10
    e.error.end_column = 42
    d = Diagnostics(endpoint=None)
    assert d.to_error(e) == {
        'range': {
            'start': {'line': 0, 'character': 10},
            'end': {'line': 0, 'character': 42},
        },
        'message': e.short_message(),
        'severity': DiagnosticSeverity.Error
    }


def test_run_empty(magic, patch):
    endpoint = magic()
    patch.object(Diagnostics, 'to_error')
    patch.object(Api, 'loads')
    d = Diagnostics(endpoint=endpoint)
    doc = Document(uri='.my.uri.', text='a = 0')
    d.run(ws=magic(), doc=doc)
    endpoint.notify.assert_called_with('textDocument/publishDiagnostics', {
        'uri': doc.uri,
        'diagnostics': [],
    })


def test_run_story_error(magic, patch):
    endpoint = magic()
    se = StoryError(None, None)
    patch.init(Story)
    patch.object(Diagnostics, 'to_error')
    patch.object(Api, 'loads', side_effect=se)
    d = Diagnostics(endpoint=endpoint)
    doc = Document(uri='.my.uri.', text='a = 0')
    d.run(ws=magic(), doc=doc)
    d.to_error.assert_called_with(se)
    endpoint.notify.assert_called_with('textDocument/publishDiagnostics', {
        'uri': doc.uri,
        'diagnostics': [Diagnostics.to_error()],
    })
