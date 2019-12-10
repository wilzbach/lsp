from sls.completion.items.item import (
    CompletionItem,
    CompletionItemKind,
    InsertTextFormat,
    SortGroup,
)

from .types import TypeMappings


class Event(CompletionItem):
    """
    A service event completion item.
    """

    def __init__(self, event):
        self.event = event

    def _text_edit(self):
        """
        Include required arguments in the service event snippet.
        """
        text_edit = f"{self.event.name()}"
        pos = 1
        for arg in self.event.args():
            if arg.required():
                ty = TypeMappings.get_type_string(arg.type())
                text_edit += f" {arg.name()}:${{{pos}:<{ty}>}}"
                pos += 1

        # include a space even when there are no required args
        if pos == 1:
            text_edit += " "

        return text_edit

    def to_completion(self, context):
        detail = self.event.help().split("\n")[0]
        return self.completion_build(
            label=self.event.name(),
            detail=f"Event: {detail}",
            text_edit=self._text_edit(),
            insert_text_format=InsertTextFormat.Snippet,
            documentation=self.event.help(),
            completion_kind=CompletionItemKind.Unit,
            context=context,
            sort_group=SortGroup.Event,
        )
