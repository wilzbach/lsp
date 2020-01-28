from .completion.context import CompletionContext
from .logging import logger

log = logger(__name__)


class Click:
    def __init__(self, completion):
        self._completion = completion

    def click(self, ws, doc, pos):
        completion = self._completion.complete(ws, doc, pos)["items"]
        context = CompletionContext(ws=ws, doc=doc, pos=pos)
        word = context.full_word()
        for item in completion:
            if item["label"] == word:
                del item["textEdit"]
                del item["sortText"]
                del item["documentation"]
                del item["insertTextFormat"]
                return item

        return {"detail": "UNKNOWN"}
