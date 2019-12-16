from sls.completion.items.base_function import BaseFunctionCompletionItem
from sls.completion.items.item import SortGroup
from sls.spec import CompletionItemKind, InsertTextFormat, MarkupKind


class CompletionBuiltin(BaseFunctionCompletionItem):
    """
    A builtin completion item.
    """

    def __init__(self, word, name, builtins):
        self.word = word
        self.builtins = builtins
        self.name = name

        # aggregate multiple builtins for the same name
        self.doc = []
        self.detail = []
        for b in builtins:
            desc = b.pretty().replace("`", "")
            self.detail.append(desc)
            if len(builtins) == 1:
                # no duplication for mutations without overloads
                desc = ""
            else:
                desc = f"### {desc}"
                desc += "\n"

            desc += b.desc()
            self.doc.append(desc)
        self.doc = "\n\n".join(self.doc)
        self.detail = "\n".join(self.detail)
        self.full_text = f"{self.word}.{self.name}"
        self.insert_name = self.full_text

    def args(self):
        return self.builtins[0].args()

    def to_completion(self, context):
        """
        Returns a LSP representation.
        """
        return self.completion_build(
            label=self.name,
            text_edit=self._text_edit(),
            detail=self.detail,
            documentation=self.doc,
            documentation_kind=MarkupKind.Markdown,
            completion_kind=CompletionItemKind.Method,
            insert_text_format=InsertTextFormat.Snippet,
            context=context,
            filter_text=self.full_text,
            sort_group=SortGroup.Builtin,
        )
