from unittest.mock import call

from pytest import raises

import sentry_sdk

import sls.sentry as sentry


def test_sentry_handle_exec(patch):
    patch.object(sentry_sdk, "capture_exception")
    ex = Exception("ex")
    with raises(Exception) as e:
        sentry.handle_exception(ex)
    assert e.value == ex


def test_sentry_handle_exec_dsn(patch):
    patch.object(sentry_sdk, "capture_exception")
    patch.object(sentry, "sentry_dsn", return_value="")
    e = Exception("")
    sentry.handle_exception(e)
    assert sentry_sdk.capture_exception.call_args == call(e)
