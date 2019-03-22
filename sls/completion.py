import logging

from .spec import CompletionItemKind


log = logging.getLogger(__name__)


class Completion():
    def __init__(self):
        self.service_list = [
            self.to_item('http', 'A HTTP service', 'Does HTTP'),
            self.to_item('log', 'A logging service', 'Does logging'),
            self.to_item('email', 'A Email service', 'Does emails'),
        ]

    """
    Builds a completion list
    """
    def complete(self, ws, doc, position):
        """"
        See the LSP Protocol on Completion [1].
        [1] https://microsoft.github.io/language-server-protocol/specification#textDocument_completion
        """  # noqa
        word = doc.word_on_cursor(position)
        log.info('Word on cursor: %s', word)
        # get last word
        items = self.service_list
        return {
            # Indicates that the list it not complete.
            # Further typing should result in recomputing this list.
            'isIncomplete': False,
            'items': items,
        }

    def to_item(self, label, detail, documentation):
        return {
            # The label of this completion item. By default
            # also the text that is inserted when selecting
            # this completion.
            'label': label,
            'kind': CompletionItemKind.Function,
            # A human-readable string with additional information
            'detail': detail,
            # A human-readable string that represents a doc-comment.
            'documentation': documentation,
            # A string that should be used when comparing this item
            # with other items. When `falsy` the label is used.
            # 'sortText': 'a',
        }
