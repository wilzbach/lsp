from storyscript.Api import Api

from .logging import logger
from .spec import DiagnosticSeverity

log = logger(__name__)


class Diagnostics:
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
        log.info("Diagnostics for: %s", doc.uri)
        errors = []
        compilation = Api.loads(doc.text())
        errors = [
            self.to_error(e)
            for e in compilation.errors()
            if not self.is_internal(e)
        ]

        self.endpoint.notify(
            "textDocument/publishDiagnostics",
            {"uri": doc.uri, "diagnostics": errors},
        )

    def is_internal(self, e):
        if e.story is None:
            return True
        return False

    def to_error(self, e):
        """
        Converts a StoryError into an error diagnostics message.
        """
        # convert from 1-based to 0-based
        line = max(0, int(e.int_line()) - 1)
        start = max(0, int(e.error.column) - 1)
        end = start + 1
        if hasattr(e.error, "end_column"):
            end = max(0, int(e.error.end_column) - 1)
        return {
            # The range at which the message applies.
            "range": {
                "start": {"line": line, "character": start},
                "end": {"line": line, "character": end},
            },
            "message": e.short_message(),
            "severity": DiagnosticSeverity.Error,
        }
