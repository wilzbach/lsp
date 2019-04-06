from sls.spec import CompletionItemKind  # noqa F401


class CompletionItem():
    """
    An individual completion item.
    """

    def to_completion(self):
        raise NotImplementedError()

    def completion_build(self, label, detail, documentation,
                         completion_kind, context, documentation_kind=None,
                         text_edit=None):
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
           # A string that should be used when comparing this item
           # with other items. When `falsy` the label is used.
           # 'sortText': 'a',
        }
        if text_edit:
            # only insert text edit if we're at the end of the document
            if len(context.line) == len(context.doc.line(context.pos.line)):
                response['textEdit'] = text_edit.dump()
        return response
