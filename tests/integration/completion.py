from pytest import mark

from sls.completion import Completion
from sls.document import Document, Position
from sls.services import ServiceRegistry


def document(text):
    doc = Document('.fake.uri.', text)
    return doc


service_registry = ServiceRegistry()
# fix the name of available services
service_registry.services = ['aservice', 'bservice', 'cservice', 'ab', 'hello']


class CompletionTest():
    def __init__(self, text):
        self.doc = document(text)

    def get_completion_for(self, pos):
        c = Completion(service_registry)
        ws = None
        return c.complete(ws, self.doc, pos)

    def test(self, pos):
        result = self.get_completion_for(Position(*pos))
        # filter only for label for now
        return [k['label'] for k in result['items']]


@mark.parametrize('text,pos,expected', [
    ('afoo bar', (0, 1), [
        'aservice', 'ab'
    ]),
    ('bfoo bar', (0, 1), [
        'bservice',
    ]),
])
def test_complete(text, pos, expected):
    test = CompletionTest(text=text)
    result = test.test(pos)
    assert result == expected
