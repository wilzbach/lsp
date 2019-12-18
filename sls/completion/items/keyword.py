from sls.completion.items.item import (
    CompletionItem,
    CompletionItemKind,
    SortGroup,
)
from sls.logging import logger
from sls.spec import InsertTextFormat

log = logger(__name__)

keywords = {
    "Map": {"detail": "Key-value collection type"},
    "List": {"detail": "Typed list"},
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

snippets = {
    "as": "as ${1:<name>}",
    "foreach": ["foreach ${1:<collection>} as ${2:<name>}", "${3:<block>}"],
    "if": "if ${1:<condition>}",
    "while": "while ${1:<condition>}",
    "Map": "Map[${1:<key_type},${2:<value_type}]",
    "List": "List[${1:<element_type}]",
}


class KeywordCompletionSymbol(CompletionItem):
    """
    A symbol completion item.
    """

    def __init__(self, keyword, sort_group=None, indent=None):
        if sort_group is None:
            sort_group = SortGroup.Keyword
        self.sort_group = sort_group
        self.keyword = keyword
        self.indent = indent
        self.indent_unit = "  "

    def to_completion(self, context):
        """
        Returns a LSP representation.
        """
        options = keywords.get(self.keyword, {})
        if self.keyword in snippets:
            snippet = snippets[self.keyword]
            if isinstance(snippet, list):
                insert_text = snippet[0]
            else:
                insert_text = snippet
            insert_text_format = InsertTextFormat.Snippet
            completion_kind = CompletionItemKind.Snippet
            if self.indent is not None:
                insert_text += f"\n{self.indent}{self.indent_unit}{snippet[1]}"
        else:
            insert_text = f"{self.keyword} "
            insert_text_format = InsertTextFormat.PlainText
            completion_kind = CompletionItemKind.Keyword
        detail = options.get("detail", self.keyword)
        documentation = options.get("doc", detail)
        return self.completion_build(
            label=self.keyword,
            text_edit=insert_text,
            detail=detail,
            documentation=documentation,
            completion_kind=completion_kind,
            insert_text_format=insert_text_format,
            context=context,
            sort_group=self.sort_group,
        )
