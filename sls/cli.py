import json
from os import environ

import click

from click_aliases import ClickAliasedGroup

import sentry_sdk
from sentry_sdk.integrations.tornado import TornadoIntegration


from .app import App
from .logging import configure_logging
from .version import version_ as app_version


sentry_sdk.init(
    environ.get("SENTRY_DSN", None),
    integrations=[TornadoIntegration()],
    release=app_version,
)


class Cli:
    @click.group(invoke_without_command=True, cls=ClickAliasedGroup)
    @click.pass_context
    @click.option(
        "--hub",
        default=None,
        type=click.Path(exists=True),
        help="Fix the hub service to a JSON file",
    )
    def main(context, hub):  # noqa N805
        """
        Learn more at https://github.com/storyscript/sls
        """
        if hub is None and isinstance(context.obj, str):
            # allow passing in predefined fixture as default
            hub = context.obj
        context.obj = App(hub_path=hub)
        if context.invoked_subcommand is None:
            click.echo(context.get_help())

    @staticmethod
    @main.command()
    @click.option("--host", default="127.0.0.1", help="Address to bind to")
    @click.option("--port", default=2042, help="Port to bind to")
    @click.pass_obj
    def tcp(app, host, port):
        """
        Start SLS via TCP
        """
        configure_logging(with_stdio=True)
        app.start_tcp_server(addr=host, port=port)

    @staticmethod
    @main.command()
    @click.option("--host", default="0.0.0.0", help="Address to bind to")
    @click.option(
        "--port", default=environ.get("PORT", 2042), help="Port to bind to"
    )
    @click.pass_obj
    def websocket(app, host, port):
        """
        Start SLS via websocket
        """
        configure_logging(with_stdio=True)
        app.start_websocket_server(addr=host, port=port)

    @staticmethod
    @main.command()
    @click.pass_obj
    def stdio(app):
        """
        Use stdin and stdout for communication
        """
        configure_logging(with_stdio=False)
        app.start_stdio_server()

    @staticmethod
    @main.command(aliases=["c"])
    @click.argument("path", type=click.File("r"))
    @click.option(
        "--line",
        "-l",
        default=None,
        type=int,
        help="Line number of the completion request (0-based)",
    )
    @click.option(
        "--column",
        "-c",
        default=None,
        type=int,
        help="Column number of the completion request (0-based)",
    )
    @click.pass_obj
    def complete(app, path, line, column):
        """
        Provide completion info for stories.
        """
        configure_logging(with_stdio=True)
        result = app.complete(
            "|completion|", path.read(), line=line, column=column
        )
        click.echo(json.dumps(result, indent=2, sort_keys=True))

    @staticmethod
    @main.command(aliases=["h"])
    @click.pass_context
    def help(context):
        """
        Prints this help text
        """
        click.echo(context.parent.get_help())

    @staticmethod
    @main.command(aliases=["v"])
    def version():
        """
        Prints the current version
        """
        click.echo(app_version)
