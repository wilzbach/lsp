from sls.completion.item import CompletionItem, CompletionItemKind
from sls.logging import logger

log = logger(__name__)

keywords = {
    "Map": {"detail": "Key-value collection type", "text_edit": "Map["},
    "List": {"detail": "Typed list", "text_edit": "List["},
    "boolean": {"detail": "Binary state type of 'true' and 'false'"},
    "int": {"detail": "Integer number type"},
    "float": {"detail": "Floating-point number type"},
    "string": {"detail": "Text representation type"},
    "regex": {"detail": "Regular Expression type"},
    "time": {"detail": "Time representation type"},
    "any": {"detail": "Arbitrary type"},
    "if": {"detail": "Conditional block"},
    "while": {"detail": "Repeated block until 'boolean' is 'false'"},
    "foreach": {"detail": "Execute block for each element"},
    "when": {"detail": "Execute block on an event"},
    "as": {"detail": "Aliasing"},
    "else": {"detail": "Execute block when 'if' condition is 'false'"},
    "and": {"detail": "Logical conjunction"},
    "not": {"detail": "Logical negation"},
    "or": {"detail": "Logical disjunction"},
    "to": {"detail": "Type conversion"},
    "try": {"detail": "Exception handling block"},
    "catch": {"detail": "Executed block on an exception"},
    "throw": {"detail": "Throw an exception"},
    "return": {"detail": "Return a value to caller or event"},
    "continue": {"detail": "Jump to the next iteration"},
    "break": {"detail": "Stop current flow"},
    "function": {"detail": "Declare a new function"},
    "true": {"detail": "Boolean value representing truth"},
    "false": {"detail": "Boolean value representing falsehood"},
    "null": {"detail": "Intentional absence of any value"},
}


class KeywordCompletionSymbol(CompletionItem):
    """
    A symbol completion item.
    """

    def __init__(self, keyword):
        self.keyword = keyword

    def to_completion(self, context):
        """
        Returns a LSP representation.
        """
        options = keywords.get(self.keyword, {})
        text_edit = options.get("text_edit", f"{self.keyword} ")
        detail = options.get("detail", self.keyword)
        documentation = options.get("doc", detail)
        return self.completion_build(
            label=self.keyword,
            text_edit=text_edit,
            detail=detail,
            documentation=documentation,
            completion_kind=CompletionItemKind.Keyword,
            context=context,
        )
