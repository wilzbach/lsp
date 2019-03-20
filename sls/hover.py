from .spec import CompletionItemKind


class Hover():
    """
    Generate hover information
    """
    def hover(self, ws, doc, position):
        return {'contents': '.hover.'}
