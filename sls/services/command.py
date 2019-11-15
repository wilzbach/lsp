from sls.completion.item import CompletionItem, CompletionItemKind


class Command(CompletionItem):
    """
    A service command completion item.
    """

    def __init__(self, command):
        self.command = command

    def to_completion(self, context):
        return self.completion_build(
            label=self.command.name(),
            detail=f"Command: {self.command.help()}",
            text_edit=f"{self.command.name()} ",
            documentation=self.command.help(),
            completion_kind=CompletionItemKind.Unit,
            context=context,
        )
