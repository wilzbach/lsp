from sls.services.action import Action


def test_args():
    arg1 = 1
    arg2 = 2
    args = {
        'arg1': arg1,
        'arg2': arg2,
    }
    action = Action('name', 'desc', args, {})
    action.arg('arg1') == 1
    action.arg('arg2') == 2
    assert [*action.args()] == [1, 2]


def test_events():
    e1 = 1
    e2 = 2
    events = {
        'e1': e1,
        'e2': e2,
    }
    action = Action('name', 'desc', {}, events)
    action.event('e1') == 1
    action.event('e2') == 2
    assert [*action.events()] == [1, 2]
