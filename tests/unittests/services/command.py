from sls.services.command import Command


def test_args():
    arg1 = 1
    arg2 = 2
    args = {
        'arg1': arg1,
        'arg2': arg2,
    }
    command = Command('name', 'desc', args)
    command.arg('arg1') == 1
    command.arg('arg2') == 2
    assert [*command.args()] == [1, 2]
