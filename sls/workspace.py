from .completion import Completion
from .diagnostics import Diagnostics
from .format import Formatter
from .hover import Hover


class Workspace:
    """
    Handles all open documents in the current workspace
    """
    def __init__(self, root_uri, endpoint):
        self.root_uri = root_uri
        self.endpoint = endpoint
        self.documents = {}
        self.diagnostics = Diagnostics(endpoint)
        self.completion = Completion()
        self.hovering = Hover()
        self.formatter = Formatter()

    def add_document(self, doc):
        self.documents[doc.uri] = doc
        self.diagnostics.run(self, doc)

    def remove_document(self, uri):
        del self.documents[uri]

    def update_document(self, uri, contentChanges):
        doc = self.get_document(uri)
        # TODO: only full text updates are implemented
        for contentChange in contentChanges:
            doc.update(contentChange['text'])

    def get_document(self, uri):
        # TODO: better error handling
        if uri in self.documents:
            return self.documents[uri]
        else:
            return None

    def complete(self, uri, position):
        doc = self.get_document(uri)
        return self.completion.complete(self, doc, position)

    def hover(self, uri, position):
        doc = self.get_document(uri)
        return self.hovering.hover(self, doc, position)

    def format(self, uri):
        doc = self.get_document(uri)
        return self.formatter.format(self, doc)
