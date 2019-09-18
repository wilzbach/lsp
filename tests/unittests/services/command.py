from sls.services.command import Command as CommandCompletionItem

from storyhub.sdk.service.Command import Command


def test_args(magic):
    args = {
        'arg1': {
            'name': 'foo',
            'help': 'Test arg 1',
            'type': 'int'
        },
        'arg2': {
            'name': 'bar',
            'help': 'Test arg 2',
            'type': 'int'
        },
    }
    command_dict = {
        'name': 'foobar',
        'command': {
            'help': 'Test command',
            'arguments': args,
        }
    }
    context = magic()
    expected_completion_dict = {
        'label': 'foobar',
        'kind': 11,
        'detail': 'Command: Test command',
        'documentation': 'Test command',
        'textEdit': {
            'range': {
                'start': {
                    'line': context.pos.line,
                    'character': context.pos.char - len(context.word)
                },
                'end': {
                    'line': context.pos.line,
                    'character': context.pos.char
                }
            },
            'newText': 'foobar '
        }
    }

    command = Command.from_dict(data=command_dict)
    command_completion = CommandCompletionItem(command)
    result = command_completion.to_completion(context)
    assert result == expected_completion_dict
