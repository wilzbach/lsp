from sls.completion.items.item import CompletionItem, SortGroup
from sls.spec import CompletionItemKind, InsertTextFormat


class CompletionFunction(CompletionItem):
    """
    A function completion item.
    """

    def __init__(self, function):
        self.function = function
        self.desc = function.pretty().replace("`", "")

    def _text_edit(self):
        """
        Include required arguments in the function snippet.
        """
        name = self.function.name()
        text_edit = f"{name}("

        pos = 1
        for arg, sym in self.function.args().items():
            if pos > 1:
                text_edit += " "
            ty = str(sym.type())
            text_edit += f"{arg}:${{{pos}:<{ty}>}}"
            pos += 1

        text_edit += ")"
        return text_edit

    def to_completion(self, context):
        """
        Returns a LSP representation.
        """
        name = self.function.name()
        return self.completion_build(
            label=name,
            text_edit=self._text_edit(),
            detail=self.desc,
            documentation=f"Function: {self.function.pretty()}",
            completion_kind=CompletionItemKind.Function,
            insert_text_format=InsertTextFormat.Snippet,
            context=context,
            sort_group=SortGroup.Function,
        )
