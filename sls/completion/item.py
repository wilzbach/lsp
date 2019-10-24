from sls.document import Position, Range, TextEdit
from sls.spec import CompletionItemKind, InsertTextFormat # noqa F401


class CompletionItem():
    """
    An individual completion item.
    """

    def to_completion(self):
        raise NotImplementedError()

    def text_edit(self, context, text):
        start = Position(
            line=context.pos.line,
            character=context.pos.char - len(context.word),
        )
        end = Position(
            line=context.pos.line,
            character=context.pos.char,
        )
        return TextEdit(Range(start, end), text)

    def completion_build(self, label, detail, documentation,
                         completion_kind, context, documentation_kind=None,
                         text_edit=None,
                         filter_text=None,
                         sort_text=None,
                         insert_text_format=InsertTextFormat.PlainText):
        if documentation_kind is not None:
            documentation = {
                'value': documentation,
                'kind': documentation_kind,
            }
        response = {
           # The label of this completion item. By default
           # also the text that is inserted when selecting
           # this completion.
           'label': label,
           'kind': completion_kind,
           # A human-readable string with additional information
           'detail': detail,
           # A human-readable string that represents a doc-comment.
           'documentation': documentation,
           # The format of the insert text
           'insertTextFormat': insert_text_format,
        }
        if text_edit:
            # only insert text edit if we're at the end of the document
            if len(context.line) == len(context.doc.line(context.pos.line)):
                edit = self.text_edit(context, text_edit).dump()
                response['textEdit'] = edit
        if sort_text is not None:
            # A string that should be used when comparing this item
            # with other items. When `falsy` the label is used.
            response['sortText'] = sort_text
        if filter_text is not None:
            # A string that should be used when filtering a set of
            # completion items. When `falsy` the label is used.
            response['filterText'] = filter_text
        return response
