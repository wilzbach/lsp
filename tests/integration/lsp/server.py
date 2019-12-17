from pyls_jsonrpc import streams
from pyls_jsonrpc.endpoint import Endpoint

from pytest import fixture, mark


from sls.lsp import LanguageServer


@fixture
def server(magic, patch):
    rx = magic()
    tx = magic()
    patch.init(Endpoint)
    patch.object(Endpoint, "notify")
    patch.init(streams.JsonRpcStreamReader)
    patch.init(streams.JsonRpcStreamWriter)
    patch.object(streams.JsonRpcStreamReader, "listen")
    server = LanguageServer(hub=None)
    server.start(rx, tx)
    streams.JsonRpcStreamReader.listen.assert_called()
    server.rpc_initialize(root_uri=".root_uri.")
    return server


def open_file(server, uri, text):
    server.rpc_text_document__did_open(
        text_document={"uri": uri, "text": text, "version": "1",}
    )


@mark.parametrize(
    "method,expected",
    [
        (
            "textDocument/completion",
            LanguageServer.rpc_text_document__completion,
        ),
        (
            "workspace/did_change_configuration",
            LanguageServer.rpc_workspace__did_change_configuration,
        ),
    ],
)
def test_dispatching(server, method, expected):
    server[method] == expected


def test_document_updates(server):
    doc = {"uri": ".magic."}
    server.rpc_text_document__did_open(
        text_document={"uri": doc["uri"], "text": ".dummy.", "version": "1"}
    )
    assert server.workspace.get_document(doc["uri"]).text() == ".dummy."
    server.rpc_text_document__did_change(
        text_document={"uri": doc["uri"],},
        content_changes=[{"text": ".dummy2."},],
    )
    assert server.workspace.get_document(doc["uri"]).text() == ".dummy2."


def test_completion(server):
    doc = {"uri": ".magic."}
    open_file(server, doc["uri"], "my_dummy service")
    pos = {"line": 0, "character": 2}
    items = []
    server.rpc_text_document__completion(text_document=doc, position=pos) == {
        "isIncomplete": True,
        "items": items,
    }


def test_indent(server):
    doc = {"uri": ".magic."}
    open_file(server, doc["uri"], "when foo bar")
    pos = {"line": 0, "character": 2}
    server.rpc_storyscript__indent(text_document=doc, position=pos) == {
        "indent": "  ",
    }


def test_indent_options(server):
    doc = {"uri": ".magic."}
    open_file(server, doc["uri"], "when foo bar")
    pos = {"line": 0, "character": 2}
    options = {"indent_unit": "    "}
    server.rpc_storyscript__indent(
        text_document=doc, position=pos, options=options
    ) == {
        "indent": "    ",
    }
