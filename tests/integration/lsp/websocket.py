import json

from pytest import fixture

from sls import App
from sls.lsp.websocket import sls_websocket
from sls.workspace import Workspace

from storyhub.sdk.ServiceWrapper import ServiceWrapper


@fixture
def ws(patch, magic):
    patch.init(Workspace)
    patch.object(
        ServiceWrapper, "from_json_file", return_value="ConstServiceHub"
    )

    app = App(hub_path=".hub.")
    ws = sls_websocket(app)
    patch.init(ws)
    patch.object(ws, "write_message")
    return ws()


def test_message(ws):
    ws.open()
    ws.on_message(
        json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 0,
                "method": "initialize",
                "params": {
                    "processId": 1,
                    "rootPath": None,
                    "rootUri": None,
                    "capabilities": {},
                },
            }
        )
    )
    assert ws.write_message.call_count == 1
    ws.write_message.assert_called_with(
        '{"jsonrpc": "2.0", "id": 0, '
        '"result": {"capabilities": {"completionProvider": '
        '{"resolveProvider": false, "triggerCharacters": [".", "(", " "]}, '
        '"hoverProvider": true, "documentFormattingProvider": true, '
        '"textDocumentSync": {"openClose": true, "change": 1}}}}'
    )


def test_message_error(patch, ws):
    ws.open()
    patch.object(ws._ls.endpoint, "consume")
    ws.on_message("abc")
    ws._ls.endpoint.consume.assert_not_called()


def test_check_origin(ws):
    ws.open()
    assert ws.check_origin("")


def test_on_close(ws):
    ws.open()
    ws.on_close()
