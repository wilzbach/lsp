from sls.completion.items.item import (
    CompletionItem,
    CompletionItemKind,
    InsertTextFormat,
    SortGroup,
)

from .types import TypeMappings


class Action(CompletionItem):
    """
    A service action completion item.
    """

    def __init__(self, action):
        self.action = action

    def _text_edit(self):
        """
        Include required arguments in the service action snippet.
        """
        text_edit = f"{self.action.name()}"
        pos = 1
        for arg in self.action.args():
            if arg.required():
                ty = TypeMappings.get_type_string(arg.type())
                text_edit += f" {arg.name()}:${{{pos}:<{ty}>}}"
                pos += 1

        # include a space even when there are no required args
        if pos == 1:
            text_edit += " "

        return text_edit

    def to_completion(self, context):
        detail = self.action.help().split("\n")[0]
        return self.completion_build(
            label=self.action.name(),
            detail=f"Action: {detail}",
            text_edit=self._text_edit(),
            insert_text_format=InsertTextFormat.Snippet,
            documentation=self.action.help(),
            completion_kind=CompletionItemKind.Unit,
            context=context,
            sort_group=SortGroup.Action,
        )
