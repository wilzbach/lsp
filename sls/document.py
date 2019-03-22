import io
from os import path
from urllib.parse import urlparse

from .logging import logger

log = logger(__name__)


class Document:
    """
    Holds all relevant info about an opened text document
    """

    def __init__(self, uri, text=None, version=None):
        self.uri = uri
        self._lines = []
        if text is not None:
            self.update(text)

    @classmethod
    def from_object(cls, text_document):
        doc = cls(text_document['uri'], version=text_document['version'])
        if 'text' in text_document:
            doc.update(text_document['text'])
        return doc

    @classmethod
    def from_file(cls, uri):
        log.debug(f'ws.doc.from_file: {uri}')
        u = urlparse(uri)
        abs_path = path.abspath(path.join(u.netloc, u.path))
        text = io.open(abs_path).read()
        doc = cls(uri, text=text)
        return doc

    def text(self):
        return self._text

    def update(self, text):
        # TODO: support \r\n and \r too
        self._lines = text.split('\n')
        self._text = text

    def line(self, nr):
        return self._lines[nr]

    def word_on_cursor(self, pos):
        line = self.line(pos.line).rstrip()
        cursor = pos.char
        if len(line) < cursor:
            cursor = len(line)

        buf = ''
        for c in reversed(line[:cursor]):
            if c == ' ':
                break
            buf += c

        return buf[::-1]


class Position:
    """
    Represents the position of a cursor
    """

    def __init__(self, line, character):
        """
        A position can be initialized by either a line and character or
        a position object.
        """
        self.line = line
        self.char = character

    @classmethod
    def from_object(cls, pos):
        return cls(pos['line'], pos['character'])

    def __str__(self):
        return f'Pos(l={self.line},c={self.char})'
