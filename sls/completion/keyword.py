from sls.completion.item import CompletionItem, CompletionItemKind
from sls.logging import logger

log = logger(__name__)


class KeywordCompletion:
    """
    Completion for Storyscript keywords.
    """
    def __init__(self):
        self._block_start = [
            KeywordCompletionSymbol('foreach', 'Loop'),
            KeywordCompletionSymbol('while', 'Loop'),
            KeywordCompletionSymbol('when', 'Listener'),
            KeywordCompletionSymbol('try', 'Exception'),
            KeywordCompletionSymbol('catch', 'Exception handling'),
            KeywordCompletionSymbol('if', 'Conditions'),
            KeywordCompletionSymbol('else', 'Conditions'),
            KeywordCompletionSymbol('else if', 'Conditions'),
            KeywordCompletionSymbol('function', 'Function'),
            KeywordCompletionSymbol('throw', 'Throw'),
        ]
        self._inside_block = [
            KeywordCompletionSymbol('return', 'Return'),
            KeywordCompletionSymbol('break', 'Break'),
            KeywordCompletionSymbol('throw', 'Throw'),
            KeywordCompletionSymbol('continue', 'Continue'),
        ]
        self._inline = [
            KeywordCompletionSymbol('to', 'Type conversion'),
            KeywordCompletionSymbol('as', 'Aliasing'),
            KeywordCompletionSymbol('and', 'Binary operator'),
            KeywordCompletionSymbol('or', 'Binary operator'),
            KeywordCompletionSymbol('not', 'Binary operator'),
        ]

    def complete_with(self, keyword_list, word):
        """
        Completes with all keywords from the given lists that start with word.
        """
        for s in keyword_list:
            if s.keyword.startswith(word):
                yield s

    def complete(self, context):
        line = context.line

        # first word in a line -> could be a new block
        if ' ' not in line:
            return self.complete_with(self._block_start, context.word)
        # first word in a block
        if ' ' not in line.lstrip():
            return self.complete_with(self._inside_block, context.word)

        # fall back to inline keywords
        return self.complete_with(self._inline, context.word)


class KeywordCompletionSymbol(CompletionItem):
    """
    A symbol completion item.
    """

    def __init__(self, keyword, description):
        self.keyword = keyword
        self.description = description

    def to_completion(self, context):
        """
        Returns a LSP representation.
        """
        return self.completion_build(
            label=self.keyword,
            text_edit=f'{self.keyword} ',
            detail=self.description,
            documentation='TBD',
            completion_kind=CompletionItemKind.Value,
            context=context,
        )
