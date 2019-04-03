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
                'start': {'line': 1, 'character': 5},
                'end': {'line': 1, 'character': 8},
            },
            'message': 'E0101: Variable `foo` has not been defined.',
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
