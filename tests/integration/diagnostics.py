from sls.diagnostics import Diagnostics
from sls.document import Document
from sls.spec import DiagnosticSeverity


def test_run_error(magic):
    endpoint = magic()
    d = Diagnostics(endpoint=endpoint)
    ws = magic()
    doc = Document(uri='.my.uri.', text='a = foo')
    d.run(ws, doc)
    endpoint.notify.assert_called_with('textDocument/publishDiagnostics', {
        'uri': doc.uri,
        'diagnostics': [{
            'range': {
                'start': {'line': 0, 'character': 4},
                'end': {'line': 0, 'character': 7},
            },
            'message': 'E0101: Variable `foo` has not been defined.',
            'severity': DiagnosticSeverity.Error
        }]
    })


def test_run_error_correct_line(magic):
    endpoint = magic()
    d = Diagnostics(endpoint=endpoint)
    ws = magic()
    doc = Document(uri='.my.uri.', text='a = 1\nb=')
    d.run(ws, doc)
    endpoint.notify.assert_called_with('textDocument/publishDiagnostics', {
        'uri': doc.uri,
        'diagnostics': [{
            'range': {
                'start': {'line': 1, 'character': 2},
                'end': {'line': 1, 'character': 3},
            },
            'message': 'E0007: Missing value after `=`',
            'severity': DiagnosticSeverity.Error
        }]
    })


def test_run_error_correct_column(magic):
    endpoint = magic()
    d = Diagnostics(endpoint=endpoint)
    ws = magic()
    doc = Document(uri='.my.uri.', text='a = 1\nb=$')
    d.run(ws, doc)
    endpoint.notify.assert_called_with('textDocument/publishDiagnostics', {
        'uri': doc.uri,
        'diagnostics': [{
            'range': {
                'start': {'line': 1, 'character': 2},
                'end': {'line': 1, 'character': 3},
            },
            'message': 'E0041: `$` is not allowed here',
            'severity': DiagnosticSeverity.Error
        }]
    })


def test_run_error_correct_end_column(magic):
    endpoint = magic()
    d = Diagnostics(endpoint=endpoint)
    ws = magic()
    doc = Document(uri='.my.uri.', text='a = 1\nb=car')
    d.run(ws, doc)
    endpoint.notify.assert_called_with('textDocument/publishDiagnostics', {
        'uri': doc.uri,
        'diagnostics': [{
            'range': {
                'start': {'line': 1, 'character': 2},
                'end': {'line': 1, 'character': 5},
            },
            'message': 'E0101: Variable `car` has not been defined.',
            'severity': DiagnosticSeverity.Error
        }]
    })


def test_run_no_error(magic):
    endpoint = magic()
    d = Diagnostics(endpoint=endpoint)
    ws = magic()
    doc = Document(uri='.my.uri.', text='a = 0')
    d.run(ws, doc)
    endpoint.notify.assert_called_with('textDocument/publishDiagnostics', {
        'uri': doc.uri,
        'diagnostics': [],
    })
