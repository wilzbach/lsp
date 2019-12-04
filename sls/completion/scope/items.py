from sls.completion.items.item import (
    CompletionItem,
    CompletionItemKind,
    InsertTextFormat,
)


class CompletionSymbol(CompletionItem):
    """
    A symbol completion item.
    """

    def __init__(self, symbol):
        self.symbol = symbol

    def to_completion(self, context):
        """
        Returns a LSP representation.
        """
        return self.completion_build(
            label=self.symbol.name(),
            text_edit=f"{self.symbol.name()}",
            detail=f"Symbol. {self.symbol.type()}",
            documentation="TBD",
            completion_kind=CompletionItemKind.Variable,
            context=context,
        )


class CompletionFunction(CompletionItem):
    """
    A function completion item.
    """

    def __init__(self, function):
        self.function = function
        self.desc = function.pretty().replace("`", "")

    def to_completion(self, context):
        """
        Returns a LSP representation.
        """
        name = self.function.name()
        return self.completion_build(
            label=name,
            text_edit=f"{name}($1)",
            detail=self.desc,
            documentation=f"Function: {self.function.pretty()}",
            completion_kind=CompletionItemKind.Function,
            insert_text_format=InsertTextFormat.Snippet,
            context=context,
        )


class CompletionBuiltin(CompletionItem):
    """
    A builtin completion item.
    """

    def __init__(self, word, builtin):
        self.word = word
        self.builtin = builtin
        self.desc = builtin.pretty().replace("`", "")

    def to_completion(self, context):
        """
        Returns a LSP representation.
        """
        name = self.builtin.name()
        full_text = f"{self.word}.{name}"
        return self.completion_build(
            label=name,
            text_edit=f"{full_text}($1)",
            detail=self.desc,
            documentation=f"Builtin: {name}",
            completion_kind=CompletionItemKind.Method,
            insert_text_format=InsertTextFormat.Snippet,
            context=context,
            filter_text=full_text,
        )
