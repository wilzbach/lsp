from sls.completion.items.item import CompletionItem, CompletionItemKind


class Action(CompletionItem):
    """
    A service action completion item.
    """

    def __init__(self, action):
        self.action = action

    def to_completion(self, context):
        detail = self.action.help().split("\n")[0]
        return self.completion_build(
            label=self.action.name(),
            detail=f"Action: {detail}",
            text_edit=f"{self.action.name()} ",
            documentation=self.action.help(),
            completion_kind=CompletionItemKind.Unit,
            context=context,
        )
