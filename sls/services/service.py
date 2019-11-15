from sls.completion.item import CompletionItem
from sls.spec import CompletionItemKind, MarkupKind


class Service(CompletionItem):
    """
    An individual service completion item.
    """

    def __init__(self, service_data):
        self.service_data = service_data

    def to_completion(self, context):
        return self.completion_build(
            label=self.service_data.name(),
            detail=self.service_data.service().description(),
            text_edit=f"{self.service_data.name()} ",
            documentation=self.service_data._readme,
            documentation_kind=MarkupKind.Markdown,
            completion_kind=CompletionItemKind.Method,
            context=context,
        )
