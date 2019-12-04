from sls.completion.items.item import CompletionItem, CompletionItemKind


class Event(CompletionItem):
    """
    An individual service event completion item.
    """

    def __init__(self, event):
        self.event = event

    def to_completion(self, context):
        return self.completion_build(
            label=self.event.name(),
            detail=f"Event: {self.event.help()}",
            documentation=f"Event doc: {self.event.help()}",
            completion_kind=CompletionItemKind.Unit,
            context=context,
        )
