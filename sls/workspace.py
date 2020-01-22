from .compile import SLSJSONCompiler
from .completion.complete import Completion
from .diagnostics import Diagnostics
from .document import Document
from .format import Formatter
from sls.indent.indent import Indentation
from .logging import logger
from .services.hub import ServiceHub
from .sentry import sentry_scope


log = logger(__name__)


class WorkspaceSettings:
    """
    Instance settings for a workspace instance.
    """

    indent_unit = "  "  # indent to add for a new indentation level


class Workspace:
    """
    Handles all open documents in the current workspace
    """

    def __init__(self, root_uri, endpoint=None, hub=None):
        self._root_uri = root_uri
        self._endpoint = endpoint
        self._documents = {}
        self._diagnostics = Diagnostics(endpoint)
        self._formatter = Formatter()
        self._service_registry = ServiceHub(hub=hub)
        self._completion = Completion.full(self._service_registry)
        self._indenter = Indentation(self._service_registry)
        self._compiler = SLSJSONCompiler()
        self.settings = WorkspaceSettings()

    def add_document(self, doc):
        log.debug(f"ws.doc.add: {doc.uri}")
        self._documents[doc.uri] = doc
        self.diagnostics(doc)

    def remove_document(self, uri):
        log.debug(f"ws.doc.remove: {uri}")
        del self._documents[uri]

    def update_document(self, uri, content_changes):
        log.debug(f"ws.doc.update: {uri}")
        doc = self.get_document(uri)
        # TODO: only full text updates are implemented
        for content_change in content_changes:
            doc.update(content_change["text"])

        self.diagnostics(doc)

    def get_document(self, uri):
        # TODO: better error handling
        if uri not in self._documents:
            self._documents[uri] = Document.from_file(uri)

        return self._documents[uri]

    def diagnostics(self, doc):
        if self._endpoint is not None:
            with sentry_scope(doc, action="diagnostics"):
                self._diagnostics.run(self, doc)

    def complete(self, uri, position):
        log.debug(f"ws.complete: {uri} pos={position}")
        doc = self.get_document(uri)
        with sentry_scope(doc, action="complete", uri=uri, position=position):
            return self._completion.complete(self, doc, position)

    def format(self, uri):
        log.debug(f"ws.format: {uri}")
        doc = self.get_document(uri)
        with sentry_scope(doc, action="format", uri=uri):
            return self._formatter.format(self, doc)

    def indent(self, uri, position, options):
        log.debug(f"ws.indent: {uri} pos={position}")
        doc = self.get_document(uri)
        indent_unit = options.get("indent_unit", self.settings.indent_unit)
        with sentry_scope(doc, action="indent", uri=uri, position=position):
            return self._indenter.indent(self, doc, position, indent_unit)

    def compile(self, uri, options):
        log.debug(f"ws.compile: {uri}")
        doc = self.get_document(uri)
        features = options.get("features", {})
        with sentry_scope(doc, action="compile", uri=uri):
            return self._compiler.compile(doc, features)
