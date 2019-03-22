from .logging import logger
from .spec import CompletionItemKind


log = logger(__name__)


class Completion():
    def __init__(self, service_registry):
        self.service_registry = service_registry

    """
    Builds a completion list
    """
    def complete(self, ws, doc, position):
        """"
        See the LSP Protocol on Completion [1].
        [1] https://microsoft.github.io/language-server-protocol/specification#textDocument_completion
        """  # noqa
        # get last word
        word = doc.word_on_cursor(position)
        log.info('Word on cursor: %s', word)
        services = self.service_registry.find_services(word)
        items = [self.service_to_item(s) for s in services]
        return {
            # Indicates that the list it not complete.
            # Further typing should result in recomputing this list.
            'isIncomplete': False,
            'items': items,
        }

    def service_to_item(self, service):
        return self.build_item(
            label=service.name(),
            detail=f'Detail for {service.name()}',
            documentation=f'Doc for {service.name()}'
        )

    def build_item(self, label, detail, documentation):
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
