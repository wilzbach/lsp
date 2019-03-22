import argparse
import logging
import socketserver

from .lsp import LanguageServer


log = logging.getLogger(__name__)


def load_args(parser):
    parser.description = 'Storyscript Language Server (SLS)'
    parser.add_argument(
        '--host', default='127.0.0.1',
        help='Address to bind to'
    )
    parser.add_argument(
        '--port', type=int, default=2042,
        help='Port to bind to'
    )


def start_tcp_server(addr, port, language_server):

    class SLSTCPServer(socketserver.StreamRequestHandler):

        def handle(self):
            log.info(f'Handling client connection')
            self._ls = language_server(self.rfile, self.wfile)
            self._ls.start()

    socketserver.TCPServer.allow_reuse_address = True

    with socketserver.TCPServer((addr, port), SLSTCPServer) as server:
        log.info(f'Serving SLS on ({addr}), {port})')
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        server.server_close()


def main():
    parser = argparse.ArgumentParser()
    load_args(parser)
    args = parser.parse_args()
    start_tcp_server(args.host, args.port, LanguageServer)


if __name__ == '__main__':
    main()
