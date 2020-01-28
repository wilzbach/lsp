import json
from os import environ

import click as clickpkg

from click_aliases import ClickAliasedGroup

from .app import App
from .logging import configure_logging
from .sentry import init as sentry_init
from .version import version as app_version


sentry_init()


class Cli:
    @clickpkg.group(invoke_without_command=True, cls=ClickAliasedGroup)
    @clickpkg.pass_context
    @clickpkg.option(
        "--hub",
        default=None,
        type=clickpkg.Path(exists=True),
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
            clickpkg.echo(context.get_help())

    @staticmethod
    @main.command()
    @clickpkg.option("--host", default="127.0.0.1", help="Address to bind to")
    @clickpkg.option("--port", default=2042, help="Port to bind to")
    @clickpkg.pass_obj
    def tcp(app, host, port):
        """
        Start SLS via TCP
        """
        configure_logging(with_stdio=True)
        app.start_tcp_server(addr=host, port=port)

    @staticmethod
    @main.command()
    @clickpkg.option("--host", default="0.0.0.0", help="Address to bind to")
    @clickpkg.option(
        "--port", default=environ.get("PORT", 2042), help="Port to bind to"
    )
    @clickpkg.pass_obj
    def websocket(app, host, port):
        """
        Start SLS via websocket
        """
        configure_logging(with_stdio=True)
        app.start_websocket_server(addr=host, port=port)

    @staticmethod
    @main.command()
    @clickpkg.pass_obj
    def stdio(app):
        """
        Use stdin and stdout for communication
        """
        configure_logging(with_stdio=False)
        app.start_stdio_server()

    @staticmethod
    @main.command(aliases=["c"])
    @clickpkg.argument("path", type=clickpkg.File("r"))
    @clickpkg.option(
        "--line",
        "-l",
        default=None,
        type=int,
        help="Line number of the completion request (0-based)",
    )
    @clickpkg.option(
        "--column",
        "-c",
        default=None,
        type=int,
        help="Column number of the completion request (0-based)",
    )
    @clickpkg.option(
        "--short", "-s", is_flag=True, help="Shortened output",
    )
    @clickpkg.pass_obj
    def complete(app, path, line, column, short):
        """
        Provide completion info for stories.
        """
        configure_logging(with_stdio=True)
        result = app.complete(
            "|completion|", path.read(), line=line, column=column
        )
        if short:
            clickpkg.echo()
            for item in result:
                clickpkg.echo(item["label"])
        else:
            clickpkg.echo(json.dumps(result, indent=2, sort_keys=True))

    @staticmethod
    @main.command()
    @clickpkg.argument("path", type=clickpkg.File("r"))
    @clickpkg.option(
        "--line",
        "-l",
        default=None,
        type=int,
        help="Line number of the click request (0-based)",
    )
    @clickpkg.option(
        "--column",
        "-c",
        default=None,
        type=int,
        help="Column number of the click request (0-based)",
    )
    @clickpkg.option(
        "--short", "-s", is_flag=True, help="Shortened output",
    )
    @clickpkg.pass_obj
    def click(app, path, line, column, short):
        """
        Provide click info for stories.
        """
        configure_logging(with_stdio=True)
        result = app.click("|click|", path.read(), line=line, column=column)
        if short:
            clickpkg.echo()
            for item in result:
                clickpkg.echo(item["label"])
        else:
            clickpkg.echo(json.dumps(result, indent=2, sort_keys=True))

    @staticmethod
    @main.command(aliases=["h"])
    @clickpkg.pass_context
    def help(context):
        """
        Prints this help text
        """
        clickpkg.echo(context.parent.get_help())

    @staticmethod
    @main.command(aliases=["v"])
    def version():
        """
        Prints the current version
        """
        clickpkg.echo(app_version)
