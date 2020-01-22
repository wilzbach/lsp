from sls.document import Position, Range, TextEdit
from sls.spec import CompletionItemKind, InsertTextFormat  # noqa F401


class SortGroup:
    """
    Sorting prefixes for item groups.
    """

    Property = 20
    Argument = 20
    Function = 20
    Builtin = 20
    Symbol = 20
    Action = 20
    Event = 20
    Service = 40
    ContextKeyword = 70
    Keyword = 90


class CompletionItem:
    """
    An individual completion item.
    """

    def to_completion(self):
        raise NotImplementedError()

    @staticmethod
    def text_edit(context, text):
        # in existing line: do not insert whitespace
        if not context.is_cursor_at_end() and text.endswith(" "):
            text = text[:-1]

        start = Position(
            line=context.pos.line,
            character=context.pos.char - len(context.word),
        )
        end = Position(line=context.pos.line, character=context.pos.char)
        return TextEdit(Range(start, end), text)

    def word_before_cursor(self, context, label):
        """
        Returns the word before the cursor.
        Takes ':' and '.' into account too.
        Examples:
            'function foo:<completion>' -> 'foo:'
            'List[<completion>' -> 'List['
        """
        # other part of the completion word
        # e.g. 'app.ho' (token_word: 'ho' -> front_word: 'app.'
        # e.g. 'app.' (token_word: '' -> front_word: 'app.'
        front_word = context.word[
            : len(context.word) - len(context.token_word)
        ]
        if len(front_word) > 0 and front_word.endswith((":", "[", "{", ".")):
            return front_word
        return ""

    def completion_build(
        self,
        label,
        detail,
        documentation,
        completion_kind,
        context,
        sort_group,
        documentation_kind=None,
        text_edit=None,
        insert_text_format=InsertTextFormat.PlainText,
    ):
        if documentation_kind is not None:
            documentation = {
                "value": documentation,
                "kind": documentation_kind,
            }
        word_before_cursor = self.word_before_cursor(context, label)
        response = {
            # The label of this completion item. By default
            # also the text that is inserted when selecting
            # this completion.
            "label": label,
            "kind": completion_kind,
            # A human-readable string with additional information
            "detail": detail,
            # A human-readable string that represents a doc-comment.
            "documentation": documentation,
            # The format of the insert text
            "insertTextFormat": insert_text_format,
        }
        if text_edit:
            edit = self.text_edit(
                context, word_before_cursor + text_edit
            ).dump()
            response["textEdit"] = edit

        response["sortText"] = f"{sort_group}-{label}"

        if len(word_before_cursor) > 0:
            # Monaco filters words based on the full word currently under the
            # editor cursor. For some reason, it takes ':', '.' into account
            # when detecting the current word.
            response["filterText"] = word_before_cursor + label

        return response
