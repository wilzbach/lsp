from sls.completion.items.item import CompletionItem, SortGroup
from sls.spec import CompletionItemKind, InsertTextFormat, MarkupKind


class CompletionBuiltin(CompletionItem):
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

    def _text_edit(self):
        """
        Include required arguments in the builtin snippet.
        """
        text_edit = f"{self.full_text}("

        builtin = self.builtins[0]

        pos = 1
        for arg, sym in builtin.args().items():
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
