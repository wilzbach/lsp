from .spec import DiagnosticSeverity


class Diagnostics():
    """
    Run diagnostics on a Storyscript file
    """
    def __init__(self, endpoint):
        self.endpoint = endpoint

    def run(self, ws, doc):
        self.endpoint.notify('textDocument/publishDiagnostics', {
            'uri': doc.uri,
            'diagnostics': [{
                # The range at which the message applies.
                'range': {
                    'start': {'line': 0, 'character': 0},
                    'end': {'line': 1, 'character': 0},
                },
                'message': 'Invalid Storyscript code',
                'severity': DiagnosticSeverity.Error
            }]
        })
