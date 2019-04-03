import argparse
import socketserver
import sys

from .logging import configure_logging, logger
from .lsp import LanguageServer
from .version import version_


log = logger(__name__)


def load_args(parser):
    """
    Adds all available options to a parser instance.
    """
    parser.description = 'Storyscript Language Server (SLS)'
    parser.add_argument(
        '--host', default='127.0.0.1',
        help='Address to bind to'
    )
    parser.add_argument(
        '--port', type=int, default=2042,
        help='Port to bind to'
    )
    parser.add_argument(
        '--stdio', action='store_true',
        help='Use stdin and stdout for communication'
    )
    parser.add_argument(
        '--version', action='store_true',
        help='Print the version number'
    )


def start_tcp_server(addr, port, language_server):
    """
    Spawns language servers for each opened socket connection.
    """

    class SLSTCPServer(socketserver.StreamRequestHandler):

        def handle(self):
            log.info(f'Client connection initiated')
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


def start_stdio_server(language_server):
    """
    Spawns a language server which reads from stdin and
    communicates via stdout.
    """
    ls = language_server(sys.stdin.buffer, sys.stdout.buffer)
    ls.start()


def cli():
    """
    Entrypoint for the CLI.
    """
    parser = argparse.ArgumentParser()
    load_args(parser)
    args = parser.parse_args()
    main(args)


def main(args):
    """
    Main entrypoint for the program.
    """
    configure_logging(with_stdio=not args.stdio)
    if args.version:
        print(version_)
    elif args.stdio:
        start_stdio_server(LanguageServer)
    else:
        start_tcp_server(args.host, args.port, LanguageServer)


if __name__ == '__main__':
    cli()
