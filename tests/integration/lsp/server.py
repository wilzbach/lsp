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
    open_file(server, doc["uri"], "my_dummy service ")
    pos = {"line": 0, "character": 16}
    items = []
    assert server.rpc_text_document__completion(
        text_document=doc, position=pos
    ) == {"isIncomplete": False, "items": items}


def test_click(server):
    doc = {"uri": ".magic."}
    open_file(server, doc["uri"], "redis increment")
    pos = {"line": 0, "character": 8}
    assert server.rpc_text_document__click(
        text_document=doc, position=pos
    ) == {
        "detail": "Action: Increments a number stored at 'key'.",
        "kind": 11,
        "label": "increment",
    }


def test_click_unknown(server):
    doc = {"uri": ".magic."}
    open_file(server, doc["uri"], "redis unknown")
    pos = {"line": 0, "character": 8}
    assert server.rpc_text_document__click(
        text_document=doc, position=pos
    ) == {"detail": "UNKNOWN",}


def test_indent(server):
    doc = {"uri": ".magic."}
    open_file(server, doc["uri"], "while true")
    pos = {"line": 0, "character": 10}
    assert server.rpc_text_document__indent(
        text_document=doc, position=pos
    ) == {
        "textEdits": [
            {
                "newText": "\n  ",
                "range": {
                    "end": {"character": 10, "line": 0},
                    "start": {"character": 10, "line": 0},
                },
            }
        ],
        "indent": "  ",
    }


def test_indent_options(server):
    doc = {"uri": ".magic."}
    open_file(server, doc["uri"], 'when http server listen path:"/"')
    pos = {"line": 0, "character": 32}
    options = {"indent_unit": "    "}
    assert server.rpc_text_document__indent(
        text_document=doc, position=pos, options=options
    ) == {
        "textEdits": [
            {
                "newText": "\n    ",
                "range": {
                    "end": {"character": 32, "line": 0},
                    "start": {"character": 32, "line": 0},
                },
            }
        ],
        "indent": "    ",
    }


def test_rpc_exit(server, patch):
    patch.object(Endpoint, "shutdown")
    patch.object(streams.JsonRpcStreamReader, "close")
    patch.object(streams.JsonRpcStreamWriter, "close")
    server.rpc_exit()
    server.endpoint.shutdown.assert_called()
    server._jsonrpc_stream_reader.close.assert_called()
    server._jsonrpc_stream_writer.close.assert_called()


def test_compile(server):
    doc = {"uri": ".magic."}
    open_file(server, doc["uri"], "a = 1")
    output = server.rpc_storyscript__compile(text_document=doc)
    del output["result"]["version"]
    assert output == {
        "errors": [],
        "deprecations": [],
        "success": True,
        "result": {
            "functions": {},
            "services": [],
            "tree": {
                "1": {
                    "method": "expression",
                    "ln": "1",
                    "col_start": "1",
                    "col_end": "6",
                    "output": None,
                    "name": ["a"],
                    "service": None,
                    "command": None,
                    "function": None,
                    "args": [{"$OBJECT": "int", "int": 1}],
                    "enter": None,
                    "exit": None,
                    "parent": None,
                    "src": "a = 1",
                }
            },
            "entrypoint": "1",
        },
    }


def test_compile_error(server):
    doc = {"uri": ".magic."}
    open_file(server, doc["uri"], "a = $")
    output = server.rpc_storyscript__compile(text_document=doc)
    assert output == {
        "errors": [
            {
                "code": "E0041",
                "hint": "`$` is not allowed here",
                "position": {"column": 5, "end_column": 6, "line": 1},
            },
        ],
        "deprecations": [],
        "success": False,
        "result": None,
    }


def test_compile_error_features(server):
    doc = {"uri": ".magic."}
    # allow global variables to be writable
    options = {"features": {"globals": True}}
    open_file(server, doc["uri"], "a = 1\na = 2")
    output = server.rpc_storyscript__compile(
        text_document=doc, options=options
    )
    del output["result"]
    assert output == {
        "errors": [],
        "deprecations": [],
        "success": True,
    }


def test_compile_deprecation(server):
    doc = {"uri": ".magic."}
    open_file(server, doc["uri"], "a = [1,2]\nb = a[0:2]")
    output = server.rpc_storyscript__compile(text_document=doc)
    del output["result"]
    assert output == {
        "errors": [],
        "deprecations": [
            {
                "code": "D0002",
                "hint": "Ranges are deprecated.",
                "position": {"column": 7, "end_column": 10, "line": 2},
            },
        ],
        "success": True,
    }
