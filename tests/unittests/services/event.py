from sls.services.event import Event as EventCompletionItem

from storyhub.sdk.service.Event import Event


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
    event_dict = {
        'name': 'foobar',
        'event': {
            'help': 'Test event',
            'arguments': args,
        }
    }
    context = magic()
    expected_completion_dict = {
        'label': 'foobar',
        'kind': 11,
        'detail': 'Event: Test event',
        'documentation': 'Event doc: Test event',
        'insertTextFormat': 1,
    }

    event = Event.from_dict(data=event_dict)
    event_completion = EventCompletionItem(event)
    result = event_completion.to_completion(context)
    assert result == expected_completion_dict
