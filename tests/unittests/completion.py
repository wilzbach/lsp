from sls.completion import Completion
from sls.document import Document
from sls.services import ServiceRegistry


def test_complete(magic, patch):
    patch.init(ServiceRegistry)
    patch.init(Document)
    patch.object(ServiceRegistry, 'find_services')
    patch.object(Completion, 'service_to_item')
    patch.object(Document, 'word_on_cursor')
    registry = ServiceRegistry()
    c = Completion(registry)
    doc = Document()
    ws = magic()
    pos = magic()
    result = c.complete(ws, doc, pos)
    doc.word_on_cursor.assert_called_with(pos)
    registry.find_services.assert_called_with(Document.word_on_cursor())
    items = []
    assert result == {
        'isIncomplete': False,
        'items': items,
    }
