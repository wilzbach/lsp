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


def test_sentry_scope(patch, magic):
    scope = magic()
    doc = magic()
    doc.text.return_value = ".doc."
    patch.object(sentry_sdk, "configure_scope")
    sentry_sdk.configure_scope.return_value.__enter__.return_value = scope
    with sentry.sentry_scope(doc=doc, action=".action."):
        pass
    scope.set_extra.assert_called_with("doc", ".doc.")
    scope.set_tag.assert_called_with("sls_action", ".action.")


def test_sentry_scope_pos(patch, magic):
    scope = magic()
    doc = magic()
    doc.text.return_value = ".doc."
    patch.object(sentry_sdk, "configure_scope")
    sentry_sdk.configure_scope.return_value.__enter__.return_value = scope
    with sentry.sentry_scope(
        doc=doc, action=".action.", position=".pos.", uri=".uri."
    ):
        pass
    scope.set_tag.assert_called_with("sls_action", ".action.")
    scope.set_extra.assert_has_calls(
        [
            call("doc", ".doc."),
            call("uri", ".uri."),
            call("position", ".pos."),
        ]
    )
