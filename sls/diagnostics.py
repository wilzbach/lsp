from storyscript.Api import Api
from storyscript.exceptions import StoryError

from .logging import logger
from .spec import DiagnosticSeverity

log = logger(__name__)


class Diagnostics():
    """
    Run diagnostics on a Storyscript file
    """
    def __init__(self, endpoint):
        self.endpoint = endpoint

    # FUTURE: should happen in a different thread
    # FUTURE: should be throttled
    def run(self, ws, doc):
        """
        Run diagnostics on a document.
        """
        log.info('Diagnostics for: %s', doc.uri)
        errors = []
        try:
            Api.loads(doc.text())
        except StoryError as e:
            errors = [self.to_error(e)]

        self.endpoint.notify('textDocument/publishDiagnostics', {
            'uri': doc.uri,
            'diagnostics': errors
        })

    def to_error(self, e):
        """
        Converts a StoryError into an error diagnostics message.
        """
        line = e.int_line()
        start = int(e.error.column)
        end = start + 1
        if hasattr(e.error, 'end_column'):
            end = int(e.error.end_column)
        return {
            # The range at which the message applies.
            'range': {
                'start': {'line': line, 'character': start},
                'end': {'line': line, 'character': end},
            },
            'message': e.short_message(),
            'severity': DiagnosticSeverity.Error
        }
