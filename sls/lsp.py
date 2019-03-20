import logging

from pyls_jsonrpc import dispatchers, endpoint, streams

from .spec import TextDocumentSyncKind
from .document import Document
from .workspace import Workspace

log = logging.getLogger(__name__)

MAX_WORKERS = 32


class LanguageServer(dispatchers.MethodDispatcher):
    """
    JSON RPC method dispatcher for the language server protocol.
    Method names are computed by converting camel case to snake case,
    slashes with double underscores, and removing dollar signs.
    """

    def __init__(self, rx, tx):
        self._jsonrpc_stream_reader = streams.JsonRpcStreamReader(rx)
        self._jsonrpc_stream_writer = streams.JsonRpcStreamWriter(tx)
        self.endpoint = endpoint.Endpoint(
            self,
            self._jsonrpc_stream_writer.write,
            max_workers=MAX_WORKERS,
        )

    def start(self):
        """Entry point for the server."""
        self._jsonrpc_stream_reader.listen(self.endpoint.consume)

    def build_capabilties(self):
        obj = {}
        # TODO: add more capabilities here
        obj['completionProvider'] = {
            # The server provides support to resolve additional information
            # for a completion item.
            'resolveProvider': False,
            # Characters that trigger completion automatically.
            'triggerCharacters': ['.']
        }
        obj['hoverProvider'] = True
        obj['documentFormattingProvider'] = True
        obj['textDocumentSync'] = {
            # Open and close notifications are sent to the server
            'openClose': True,
            # Change notifications are sent to the server
            'change': TextDocumentSyncKind.Full,
        }
        return obj

    def m_initialize(self, processId=None, rootUri=None, rootPath=None,
                     initializationOptions=None, **_kwargs):
        log.debug(f'Initialized with pid={processId}% root_uri={rootUri} '
                  f'rootPath={rootPath} options={initializationOptions}%')
        self.workspace = Workspace(rootUri, self.endpoint)
        # TODO: load user config here
        return {
            'capabilities': self.build_capabilties()
        }

    def m_initialized(self, **_kwargs):
        pass

    def m_text_document__completion(self, textDocument=None,
                                    position=None, **_kwargs):
        return self.workspace.complete(textDocument['uri'], position)

    def m_text_document__hover(self, textDocument=None,
                               position=None, **_kwargs):
        return self.workspace.hover(textDocument['uri'], position)

    def m_text_document__formatting(self, textDocument=None,
                                    _options=None, **_kwargs):
        return self.workspace.format(textDocument['uri'])

    def m_text_document__did_open(self, textDocument=None, **_kwargs):
        self.workspace.add_document(Document(textDocument))
        # TODO: run initial diagnostics here

    def m_text_document__did_close(self, textDocument=None, **_kwargs):
        self.workspace.remove_document(textDocument['uri'])

    def m_text_document__did_change(self, contentChanges=None,
                                    textDocument=None, **_kwargs):
        # TODO: use incremental changes
        self.workspace.update_document(textDocument['uri'], contentChanges)
        # TODO: relint the document

    def m_text_document__did_save(self, textDocument=None, **_kwargs):
        # TODO: relint
        pass

    def m_workspace__did_change_configuration(self, settings=None):
        # TODO
        pass

    def m_workspace__did_change_watched_files(self, changes=None, **_kwargs):
        # TODO
        pass

    def m_shutdown(self, **_kwargs):
        self._shutdown = True

    def m_exit(self, **_kwargs):
        self.endpoint.shutdown()
        self._jsonrpc_stream_reader.close()
        self._jsonrpc_stream_writer.close()
