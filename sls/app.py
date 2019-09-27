import socketserver
import sys

from storyhub.sdk.ServiceWrapper import ServiceWrapper

from .document import Document, Position
from .logging import logger
from .lsp import LanguageServer
from .workspace import Workspace


log = logger(__name__)


class App:

    def __init__(self, hub=None, hub_path=None):
        self.language_server = LanguageServer
        if isinstance(hub_path, str):
            hub = ServiceWrapper.from_json_file(hub_path)
        self.hub = hub
        self.ws = Workspace('.root.', hub=hub)

    def start_tcp_server(self, addr, port):
        """
        Spawns language servers for each opened socket connection.
        """
        _self = self

        class SLSTCPServer(socketserver.StreamRequestHandler):

            def handle(self):
                log.info(f'Client connection initiated')
                self._ls = _self.language_server(self.rfile, self.wfile,
                                                 hub=_self.hub)
                self._ls.start()

        socketserver.TCPServer.allow_reuse_address = True

        with socketserver.TCPServer((addr, port), SLSTCPServer) as server:
            log.info(f'Serving SLS on ({addr}), {port})')
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
            server.server_close()

    def start_stdio_server(self):
        """
        Spawns a language server which reads from stdin and
        communicates via stdout.
        """
        ls = self.language_server(sys.stdin.buffer, sys.stdout.buffer,
                                  hub=self.hub)
        ls.start()

    def complete(self, uri, text, line=None, column=None):
        uri = 'complete:/' + uri
        doc = Document(uri, text=text)
        # jump to the end of the story if no line/colum were set
        if line is None:
            # TODO
            line = max(0, doc.nr_lines() - 2)
        if column is None:
            column = max(0, len(doc.line(line)))

        position = Position(line=line, character=column)
        self.ws.add_document(doc)
        response = self.ws.complete(uri, position=position)['items']
        self.ws.remove_document(uri)
        return response
