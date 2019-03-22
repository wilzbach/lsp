from sls.services.event import Event


def test_args():
    arg1 = 1
    arg2 = 2
    args = {
        'arg1': arg1,
        'arg2': arg2,
    }
    event = Event('name', 'desc', args)
    event.arg('arg1') == 1
    event.arg('arg2') == 2
    assert [*event.args()] == [1, 2]


def test_name():
    event = Event('name', 'desc', {})
    assert event.name() == 'name'
