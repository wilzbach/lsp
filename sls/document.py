import logging

log = logging.getLogger(__name__)


class Document:
    """
    Holds all relevant info about an opened text document
    """

    def __init__(self, textDocument):
        log.info("textDocument: %s", textDocument)
        self.uri = textDocument['uri']
        self.version = textDocument['version']
        self._lines = []

        if 'text' in textDocument:
            self.update(textDocument['text'])

    def text(self):
        return self._text

    def update(self, text):
        # TODO: support \r\n and \r too
        self._lines = text.split('\n')
        self._text = text

    def line(self, nr):
        return self._lines[nr]

    def word_on_cursor(self, position):
        line = self.line(position['line']).rstrip()
        cursor = position['character']
        if len(line) > cursor:
            cursor = len(line)

        buf = ""
        for c in reversed(line[:cursor]):
            if c == ' ':
                break
            buf += c

        return buf[::-1]
