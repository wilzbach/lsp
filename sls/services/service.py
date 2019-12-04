from sls.completion.items.item import CompletionItem
from sls.spec import CompletionItemKind, MarkupKind


class Service(CompletionItem):
    """
    An individual service completion item.
    """

    def __init__(self, service_data):
        self.service_data = service_data
        self._name = self.service_data.name

    def to_completion(self, context):
        return self.completion_build(
            label=self.name(),
            detail=self.service_data.service().description(),
            text_edit=f"{self.name()} ",
            documentation=self.service_data._readme,
            documentation_kind=MarkupKind.Markdown,
            completion_kind=CompletionItemKind.Method,
            context=context,
        )

    def name(self):
        return self._name

    def set_name(self, name):
        self._name = name
