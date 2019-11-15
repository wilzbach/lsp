import sys
from socketserver import StreamRequestHandler

from pytest import mark

from sls import App
from sls.app import SLSApplication, tornado
from sls.lsp import LanguageServer
from sls.workspace import Workspace

from storyhub.sdk.ServiceWrapper import ServiceWrapper


def test_init(patch):
    """
    Tests that an SLS App gets properly initialized.
    """
    patch.init(Workspace)
    app = App()
    Workspace.__init__.assert_called_with(".root.", hub=None)
    assert app.hub is None
    assert isinstance(app.ws, Workspace)


def test_init_hub_path(patch):
    """
    Tests that an SLS App with a Hub Path gets properly initialized.
    """
    patch.init(Workspace)
    patch.object(
        ServiceWrapper, "from_json_file", return_value="ConstServiceHub"
    )
    hub_path = ".hub.path."
    app = App(hub_path=hub_path)
    ServiceWrapper.from_json_file.assert_called_with(hub_path)
    Workspace.__init__.assert_called_with(
        ".root.", hub=ServiceWrapper.from_json_file()
    )
    assert isinstance(app.ws, Workspace)
    assert app.hub == "ConstServiceHub"


def test_stdio(patch):
    """
    Tests whether starting a stdio server works.
    """
    patch.init(Workspace)
    patch.init(LanguageServer)
    patch.object(
        ServiceWrapper, "from_json_file", return_value="ConstServiceHub"
    )
    patch.object(LanguageServer, "start")
    app = App(hub_path=".hub.")
    app.start_stdio_server()
    LanguageServer.__init__.assert_called_with(hub="ConstServiceHub")
    LanguageServer.start.assert_called_with(
        sys.stdin.buffer, sys.stdout.buffer
    )


@mark.parametrize("keyboard_abort", [False, True])
def test_tcp(patch, magic, keyboard_abort):
    """
    Tests whether starting a tcp server works.
    """
    server = magic()
    if keyboard_abort:
        server.serve_forever.side_effect = KeyboardInterrupt()
    did_exit = False

    class FakeServer:
        def __init__(self, arg_port, cls):
            assert arg_port == (".addr.", ".port.")
            self.cls = cls

        def __enter__(self):
            LanguageServer.start.assert_not_called()
            tcp_server = self.cls()
            tcp_server.rfile = "rfile"
            tcp_server.wfile = "wfile"
            tcp_server.handle()
            return server

        def __exit__(self, a, b, c):
            nonlocal did_exit
            did_exit = True

    patch.init(Workspace)
    patch.object(
        ServiceWrapper, "from_json_file", return_value="ConstServiceHub"
    )

    patch.init(LanguageServer)
    patch.object(LanguageServer, "start")

    patch("socketserver.TCPServer", FakeServer)
    patch.init(StreamRequestHandler)

    app = App(hub_path=".hub.")
    app.start_tcp_server(addr=".addr.", port=".port.")
    assert FakeServer.allow_reuse_address

    server.serve_forever.assert_called()
    server.server_close.assert_called()
    LanguageServer.__init__.assert_called_with(hub="ConstServiceHub")
    LanguageServer.start.assert_called_with("rfile", "wfile")
    assert did_exit


def test_websocket(patch, magic):
    """
    Tests whether starting a tcp server works.
    """
    patch.init(Workspace)
    patch.object(
        ServiceWrapper, "from_json_file", return_value="ConstServiceHub"
    )

    patch.init(LanguageServer)
    patch.object(LanguageServer, "start")

    patch.object(SLSApplication, "listen")
    patch.object(tornado.ioloop.IOLoop, "current")

    app = App(hub_path=".hub.")
    app.start_websocket_server(addr=".addr.", port=".port.")

    SLSApplication.listen.assert_called_with(".port.")
    tornado.ioloop.IOLoop.current().start.assert_called()
