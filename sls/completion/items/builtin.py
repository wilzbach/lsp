from sls.completion.items.item import CompletionItem
from sls.spec import CompletionItemKind, InsertTextFormat


class CompletionBuiltin(CompletionItem):
    """
    A builtin completion item.
    """

    def __init__(self, word, name, builtins):
        self.word = word
        self.builtins = builtins
        self.name = name

        # aggregate multiple builtins for the same name
        self.desc = []
        for b in builtins:
            self.desc.append(b.pretty().replace("`", ""))
        self.desc = "\n".join(self.desc)

    def to_completion(self, context):
        """
        Returns a LSP representation.
        """
        full_text = f"{self.word}.{self.name}"
        return self.completion_build(
            label=self.name,
            text_edit=f"{full_text}($1)",
            detail=self.desc,
            documentation=f"Builtin: {self.name}",
            completion_kind=CompletionItemKind.Method,
            insert_text_format=InsertTextFormat.Snippet,
            context=context,
            filter_text=full_text,
        )
