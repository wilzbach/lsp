from .completion import Completion
from .diagnostics import Diagnostics
from .document import Document
from .format import Formatter
from .hover import Hover
from .logging import logger
from .services import ServiceRegistry


log = logger(__name__)


class Workspace:
    """
    Handles all open documents in the current workspace
    """
    def __init__(self, root_uri, endpoint):
        self.root_uri = root_uri
        self.endpoint = endpoint
        self.documents = {}
        self.diagnostics = Diagnostics(endpoint)
        self.hovering = Hover()
        self.formatter = Formatter()
        self.service_registry = ServiceRegistry()
        self.completion = Completion(self.service_registry)

    def add_document(self, doc):
        log.debug(f'ws.doc.add: {doc.uri}')
        self.documents[doc.uri] = doc
        self.diagnostics.run(self, doc)

    def remove_document(self, uri):
        log.debug(f'ws.doc.remove: {uri}')
        del self.documents[uri]

    def update_document(self, uri, content_changes):
        log.debug(f'ws.doc.update: {uri}')
        doc = self.get_document(uri)
        # TODO: only full text updates are implemented
        for content_change in content_changes:
            doc.update(content_change['text'])

    def get_document(self, uri):
        # TODO: better error handling
        if uri not in self.documents:
            self.documents[uri] = Document.from_file(uri)

        return self.documents[uri]

    def complete(self, uri, position):
        log.debug(f'ws.complete: {uri} pos={position}')
        doc = self.get_document(uri)
        return self.completion.complete(self, doc, position)

    def hover(self, uri, position):
        log.debug(f'ws.hover: {uri} pos={position}')
        doc = self.get_document(uri)
        return self.hovering.hover(self, doc, position)

    def format(self, uri):
        log.debug(f'ws.format: {uri}')
        doc = self.get_document(uri)
        return self.formatter.format(self, doc)
