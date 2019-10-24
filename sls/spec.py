"""
Python header for the Language Server Protocol
See: https://microsoft.github.io/language-server-protocol/specification
"""


class TextDocumentSyncKind:
    """
    Defines how the host (editor) should sync document changes
    to the language server.
    """
    # Documents should not be synced at all.
    None_ = 0
    # Documents are synced by always sending the full content of the document.
    Full = 1
    # Documents are synced by sending the full content on open.
    # After that only incremental updates to the document are
    # send.
    Incremental = 2


class CompletionItemKind:
    """
    The kind of a completion entry.
    """
    Text = 1
    Method = 2
    Function = 3
    Constructor = 4
    Field = 5
    Variable = 6
    Class = 7
    Interface = 8
    Module = 9
    Property = 10
    Unit = 11
    Value = 12
    Enum = 13
    Keyword = 14
    Snippet = 15
    Color = 16
    File = 17
    Reference = 18
    Folder = 19
    EnumMember = 20
    Constant = 21
    Struct = 22
    Event = 23
    Operator = 24
    TypeParameter = 25


class DiagnosticSeverity:
    """
    The diagnostic's severity.
    """

    # Reports an error.
    Error = 1

    # Reports a warning.
    Warning = 2

    # Reports an information.
    Information = 3

    # Reports a hint.
    Hint = 4


class MarkupKind:
    """
    Markup format kind for content.
    """
    PlainText = 'plaintext'
    Markdown = 'markdown'


class InsertTextFormat:
    """
    Defines whether the insert text in a completion item should be interpreted
    as plain text or a snippet.
    """
    PlainText = 1
    Snippet = 2
