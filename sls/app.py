from contextlib import contextmanager
import socketserver
import sys

from storyhub.sdk.ServiceWrapper import ServiceWrapper

import tornado
import tornado.ioloop

from .document import Document, Position
from .logging import logger
from .lsp import LanguageServer
from .lsp.websocket import SLSApplication
from .workspace import Workspace


log = logger(__name__)


class App:
    def __init__(self, hub=None, hub_path=None):
        self.language_server = LanguageServer
        if isinstance(hub_path, str):
            hub = ServiceWrapper.from_json_file(hub_path)
        self.hub = hub
        self.ws = Workspace(".root.", hub=hub)

    def start_tcp_server(self, addr, port):
        """
        Spawns language servers for each opened socket connection.
        """
        _self = self

        class SLSTCPServer(socketserver.StreamRequestHandler):
            def handle(self):
                log.info(f"Client connection initiated")
                self._ls = _self.language_server(hub=_self.hub)
                self._ls.start(self.rfile, self.wfile)

        socketserver.TCPServer.allow_reuse_address = True

        with socketserver.TCPServer((addr, port), SLSTCPServer) as server:
            log.info(f"Serving SLS/TCP on ({addr}, {port})")
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
            server.server_close()

    def start_websocket_server(self, addr, port):
        """
        Spawns language servers for each opened socket connection.
        """
        app = SLSApplication(self, default_host=addr)
        app.listen(port)
        log.info(f"Serving SLS/Websocket on ({addr}, {port})")
        tornado.ioloop.IOLoop.current().start()

    def start_stdio_server(self):
        """
        Spawns a language server which reads from stdin and
        communicates via stdout.
        """
        ls = self.language_server(hub=self.hub)
        ls.start(sys.stdin.buffer, sys.stdout.buffer)

    def complete(self, uri, text, line=None, column=None):
        uri = "complete:/" + uri
        with self.document(uri, text) as doc:
            position = self._position(doc, line, column)
            return self.ws.complete(uri, position=position)["items"]

    def click(self, uri, text, line=None, column=None):
        uri = "click:/" + uri
        with self.document(uri, text) as doc:
            position = self._position(doc, line, column)
            return self.ws.click(uri, position=position)

    @staticmethod
    def _position(doc, line, column):
        """
        Normalize position information.
        """
        # jump to the end of the story if no line/column were set
        if line is None:
            line = max(0, doc.nr_lines() - 2)
        if column is None:
            column = max(0, len(doc.line(line)))

        position = Position(line=line, character=column)
        return position

    @contextmanager
    def document(self, uri, text):
        doc = Document(uri, text=text)
        self.ws.add_document(doc)
        yield doc
        self.ws.remove_document(uri)
