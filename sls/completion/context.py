from sls.logging import logger

log = logger(__name__)


class CompletionContext():
    """
    Holds the reference to all information known about the request.
    """

    def __init__(self, ws, doc, pos):
        self.ws = ws
        self.doc = doc
        self.pos = pos
        self.word = doc.word_on_cursor(pos)
        self.line = doc.line_to_cursor(pos)
