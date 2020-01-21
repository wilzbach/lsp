from contextlib import contextmanager
from os import environ

import sentry_sdk
from sentry_sdk.integrations.tornado import TornadoIntegration

from .version import version as app_version


_sentry_dsn = environ.get("SENTRY_DSN", None)


def init():
    sentry_sdk.init(
        sentry_dsn(), integrations=[TornadoIntegration()], release=app_version,
    )


def sentry_dsn():
    return _sentry_dsn


def handle_exception(e):
    """
    Capture exceptions in release mode (sentry_dsn defined),
    but rethrow them in debug mode.
    """
    if sentry_dsn() is not None:
        sentry_sdk.capture_exception(e)
    else:
        raise e


@contextmanager
def sentry_scope(doc, action, uri=None, position=None):
    with sentry_sdk.configure_scope() as scope:
        scope.set_extra("doc", doc.text())
        scope.set_tag("sls_action", action)
        if uri is not None:
            scope.set_extra("uri", uri)
        if position is not None:
            scope.set_extra("position", str(position))
        yield
