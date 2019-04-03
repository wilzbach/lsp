from pytest import fixture

from sls.document import Document
from sls.workspace import Workspace


@fixture
def ws(magic):
    return Workspace(root_uri='.root_uri.', endpoint=magic())


@fixture
def doc():
    return Document('.doc_uri.', text='.doc.text.')


def test_update_doc(ws, doc, patch):
    patch.object(Workspace, 'diagnostics')
    ws.add_document(doc)
    ws.update_document(doc.uri, [{'text': '.foo.'}])
    assert ws.get_document(doc.uri).text() == '.foo.'
    assert doc.text() == '.foo.'
    Workspace.diagnostics.assert_called_with(doc)


def test_update_multiple_doc(ws, doc, patch):
    patch.object(Workspace, 'diagnostics')
    ws.add_document(doc)
    ws.update_document(doc.uri, [{'text': '.foo.'}, {'text': '.bar.'}])
    assert ws.get_document(doc.uri).text() == '.bar.'
    assert doc.text() == '.bar.'
    Workspace.diagnostics.assert_called_with(doc)
