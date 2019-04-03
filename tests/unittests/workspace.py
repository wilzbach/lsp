from pytest import fixture

from sls.completion import Completion
from sls.diagnostics import Diagnostics
from sls.document import Document
from sls.format import Formatter
from sls.hover import Hover
from sls.workspace import Workspace


@fixture
def ws(magic):
    return Workspace(root_uri='.root_uri.', endpoint=magic())


@fixture
def doc():
    return Document('.doc_uri.', text='.doc.text.')


def test_add_doc(ws, doc, patch):
    patch.object(Workspace, 'diagnostics')
    ws.add_document(doc)
    assert ws.get_document(doc.uri) == doc
    Workspace.diagnostics.assert_called_with(doc)


def test_update_doc(ws, doc, patch):
    patch.many(Workspace, ['diagnostics', 'get_document'])
    ws.add_document(doc)
    ws.update_document(doc.uri, [{'text': '.foo.'}])
    Workspace.get_document.assert_called_with(doc.uri)
    Workspace.get_document().update.assert_called_with('.foo.')
    Workspace.diagnostics.assert_called_with(Workspace.get_document())


def test_update_multiple_doc(ws, doc, patch):
    patch.many(Workspace, ['diagnostics', 'get_document'])
    ws.add_document(doc)
    ws.update_document(doc.uri, [{'text': '.foo.'}, {'text': '.bar.'}])
    Workspace.get_document.assert_called_with(doc.uri)
    Workspace.get_document().update.assert_called_with('.bar.')
    Workspace.diagnostics.assert_called_with(Workspace.get_document())


def test_diagnostics(ws, doc, patch):
    patch.object(Diagnostics, 'run')
    ws.diagnostics(doc)
    Diagnostics.run.assert_called_with(ws, doc)


def test_complete(ws, doc, patch):
    patch.object(Completion, 'complete')
    patch.object(Workspace, 'get_document')
    ws.complete('.uri.', '.pos.')
    Workspace.get_document.assert_called_with('.uri.')
    Completion.complete.assert_called_with(ws, Workspace.get_document(),
                                           '.pos.')


def test_hover(ws, doc, patch):
    patch.object(Hover, 'hover')
    patch.object(Workspace, 'get_document')
    ws.hover('.uri.', '.pos.')
    Workspace.get_document.assert_called_with('.uri.')
    Hover.hover.assert_called_with(ws, Workspace.get_document(), '.pos.')


def test_format(ws, doc, patch):
    patch.object(Formatter, 'format')
    patch.object(Workspace, 'get_document')
    ws.format('.uri.')
    Workspace.get_document.assert_called_with('.uri.')
    Formatter.format.assert_called_with(ws, Workspace.get_document())
