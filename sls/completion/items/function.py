from sls.completion.items.base_function import BaseFunctionCompletionItem
from sls.completion.items.item import SortGroup
from sls.spec import CompletionItemKind, InsertTextFormat


class CompletionFunction(BaseFunctionCompletionItem):
    """
    A function completion item.
    """

    def __init__(self, function):
        self.function = function
        self.desc = function.pretty().replace("`", "")
        self.insert_name = self.function.name()

    def args(self):
        return self.function.args()

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
