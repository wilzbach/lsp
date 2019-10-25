import json

import click
from click.testing import CliRunner

from pytest import fixture, mark

from sls import App, Cli
from sls.version import version_


@fixture
def runner():
    return CliRunner()


@fixture
def echo(patch):
    patch.object(click, 'echo')


@fixture
def app(patch):
    patch.init(App)
    patch.many(App, ['complete', 'start_tcp_server', 'start_stdio_server'])
    return App


@mark.parametrize('option', ['version', 'v'])
def test_cli_version_flag(runner, echo, option):
    """
    Ensures --version outputs the version
    """
    e = runner.invoke(Cli.main, option)
    click.echo.assert_called_with(version_)
    assert e.exit_code == 0


def test_cli_help_flag(runner, echo):
    e = runner.invoke(Cli.main, ['--help'])
    assert e.output.startswith('Usage: main')
    assert click.echo.call_count == 0
    assert e.exit_code == 0


@mark.parametrize('option', ['help', 'h'])
def test_cli_help_page(runner, echo, option):
    e = runner.invoke(Cli.main, [option])
    assert click.echo.call_count == 1
    assert click.echo.call_args[0][0].startswith('Usage: main')
    assert e.exit_code == 0


def test_cli_empty(runner, echo):
    e = runner.invoke(Cli.main, [])
    assert click.echo.call_count == 1
    assert click.echo.call_args[0][0].startswith('Usage: main')
    assert e.exit_code == 0


def test_cli_hub_flag(runner, echo, app):
    """
    Ensures --version outputs the version
    """
    with runner.isolated_filesystem():
        with open('my.hub', 'w') as f:
            f.write('Hello World!')
        e = runner.invoke(Cli.main, ['--hub=my.hub'])
        assert e.exit_code == 0
        app.__init__.assert_called_with(hub_path='my.hub')


def test_cli_hub_manual(patch, runner, echo, app, magic):
    """
    Allows to manually overwrite --hub from outside calls.
    """
    Cli.main(args=['stdio'], standalone_mode=False, obj='my.hub')
    app.__init__.assert_called_with(hub_path='my.hub')
    app.start_stdio_server.assert_called()


def test_cli_tcp(runner, echo, app):
    """
    Ensures tcp starts a server.
    """
    e = runner.invoke(Cli.main, ['tcp'])
    app.start_tcp_server.assert_called_with(addr='127.0.0.1', port=2042)
    assert e.exit_code == 0


def test_cli_tcp_port(runner, echo, app):
    """
    Ensures tcp starts a server.
    """
    e = runner.invoke(Cli.main, ['tcp', '--port=123'])
    app.start_tcp_server.assert_called_with(addr='127.0.0.1', port=123)
    assert e.exit_code == 0


def test_cli_tcp_host(runner, echo, app):
    """
    Ensures tcp starts a server.
    """
    e = runner.invoke(Cli.main, ['tcp', '--host=foo'])
    app.start_tcp_server.assert_called_with(addr='foo', port=2042)
    assert e.exit_code == 0


def test_cli_tcp_hub(runner, echo, app):
    """
    Ensures tcp starts a server.
    """
    with runner.isolated_filesystem():
        with open('my.hub', 'w') as f:
            f.write('Hello World!')
        e = runner.invoke(Cli.main, ['--hub=my.hub', 'tcp'])
        assert e.exit_code == 0
        app.__init__.assert_called_with(hub_path='my.hub')
        app.start_tcp_server.assert_called_with(addr='127.0.0.1', port=2042)


def test_cli_stdio(runner, echo, app):
    """
    Ensures stdio spawns a server.
    """
    e = runner.invoke(Cli.main, ['stdio'])
    app.start_stdio_server.assert_called()
    assert e.exit_code == 0


def test_cli_stdio_hub(runner, echo, app):
    """
    Ensures tcp starts a server.
    """
    with runner.isolated_filesystem():
        with open('my.hub', 'w') as f:
            f.write('Hello World!')
        e = runner.invoke(Cli.main, ['--hub=my.hub', 'stdio'])
        assert e.exit_code == 0
        app.__init__.assert_called_with(hub_path='my.hub')
        app.start_stdio_server.assert_called()


def test_cli_complete_missing(patch, runner, echo, app):
    """
    Ensures that the completion file exists.
    """
    e = runner.invoke(Cli.main, ['complete'])
    assert click.echo.call_count == 0
    assert e.exit_code == 2


def test_cli_complete_hub(patch, runner, echo, app):
    """
    Ensures CLI completion with a custom hub works.
    """
    patch.object(json, 'dumps')
    with runner.isolated_filesystem():
        text = 'foobar'
        with open('my.story', 'w') as f:
            f.write(text)
        with open('my.hub', 'w') as f:
            f.write('Hello World!')
        e = runner.invoke(Cli.main, ['--hub=my.hub', 'complete', 'my.story'])
        app.__init__.assert_called_with(hub_path='my.hub')
        app.complete.assert_called_with('|completion|', text,
                                        line=None, column=None)
        json.dumps.assert_called_with(app.complete(), indent=2, sort_keys=True)
        click.echo.assert_called_with(json.dumps())
        assert e.exit_code == 0


@mark.parametrize('options,expected', [
    ([], {'line': None, 'column': None}),
    (['--line', '2'], {'line': 2, 'column': None}),
    (['-l', '2'], {'line': 2, 'column': None}),
    (['--column', '3'], {'line': None, 'column': 3}),
    (['-c', '3'], {'line': None, 'column': 3}),
    (['-l', '2', '-c', '3'], {'line': 2, 'column': 3}),
])
def test_cli_complete_line_column(patch, runner, echo, app, options, expected):
    """
    Ensures CLI completion with custom line and column works.
    """
    patch.object(json, 'dumps')
    with runner.isolated_filesystem():
        text = 'foobar'
        with open('my.story', 'w') as f:
            f.write(text)
        e = runner.invoke(Cli.main, ['complete', 'my.story', *options])
        app.complete.assert_called_with('|completion|', text, **expected)
        json.dumps.assert_called_with(app.complete(), indent=2, sort_keys=True)
        click.echo.assert_called_with(json.dumps())
        assert e.exit_code == 0
