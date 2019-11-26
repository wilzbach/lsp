from os import environ

import sentry_sdk
from sentry_sdk.integrations.tornado import TornadoIntegration

from .version import version_ as app_version


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
