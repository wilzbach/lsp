from sls.completion import Completion


def test_complete_hello(magic):
    c = Completion()
    ws = magic()
    doc = magic()
    position = {'line': 0, 'character': 2}
    c.complete(ws, doc, position)
