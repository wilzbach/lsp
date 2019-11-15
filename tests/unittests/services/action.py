from sls.services.action import Action as ActionCompletionItem

from storyhub.sdk.service.Action import Action


def test_args(magic):
    args = {
        "arg1": {"name": "foo", "help": "Test arg 1", "type": "int"},
        "arg2": {"name": "bar", "help": "Test arg 2", "type": "int"},
    }
    action_dict = {
        "name": "foobar",
        "action": {"help": "Test action", "arguments": args,},
    }
    context = magic()
    expected_completion_dict = {
        "label": "foobar",
        "kind": 11,
        "detail": "Action: Test action",
        "documentation": "Test action",
        "textEdit": {
            "range": {
                "start": {
                    "line": context.pos.line,
                    "character": context.pos.char - len(context.word),
                },
                "end": {
                    "line": context.pos.line,
                    "character": context.pos.char,
                },
            },
            "newText": "foobar ",
        },
        "insertTextFormat": 1,
    }

    action = Action.from_dict(data=action_dict)
    action_completion = ActionCompletionItem(action)
    result = action_completion.to_completion(context)
    assert result == expected_completion_dict
