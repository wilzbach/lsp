from sls.Completion import Completion


def test_complete_hello():
    c = Completion()
    c.complete()
    assert 0
