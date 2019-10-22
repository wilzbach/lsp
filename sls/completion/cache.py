from collections import namedtuple

from cachetools import LRUCache

from sls.completion.item import CompletionItem, CompletionItemKind
from sls.document import Position, Range, TextEdit
from sls.logging import logger

from storyscript import loads
from storyscript.compiler.semantics.functions.FunctionTable import \
    FunctionTable
from storyscript.compiler.semantics.symbols.Scope import Scope


log = logger(__name__)

CacheOutput = namedtuple('CacheOutput', [
    'function_table', 'mutation_table', 'root_scope'
])


class ContextCache():
    """
    Cache for other global blocks which caches global context like
        - FunctionTable
        - SymbolTable (global)
    """

    def __init__(self):
        self.function_table = None
        self.mutation_table = None
        self.global_scope = None
        self.block_cache = LRUCache(1000)

    def update(self, context):
        self.global_scope = self.aggregate_scope_blocks(context)
        self.function_table = self.aggregate_function_blocks(context)
        return context.current_block()

    @staticmethod
    def compile(text):
        output = loads(text)
        if output.success():
            module = output.result().module()
            return CacheOutput(function_table=module.function_table,
                               mutation_table=module.mutation_table,
                               root_scope=module.root_scope)
        else:
            return None

    def other_blocks(self, context):
        for block in context.other_blocks():
            text = context.doc.lines(block.start, block.end)
            story_text = '\n'.join(text)
            if story_text in self.block_cache:
                result = self.block_cache[story_text]
            else:
                result = self.compile(story_text)
                self.block_cache[story_text] = result

            if result is not None:
                yield result

    def aggregate_scope_blocks(self, context):
        scope = Scope()
        for block in self.other_blocks(context):
            scope.insert_scope(block.root_scope)
        return scope

    def aggregate_function_blocks(self, context):
        fn_table = FunctionTable()
        for block in self.other_blocks(context):
            fn_table.insert_fn_table(block.function_table)
        return fn_table

    def complete_global(self, word):
        for name, symbol in self.global_scope.symbols()._symbols.items():
            if name.startswith(word):
                yield CompletionSymbol(symbol)

        for name, function in self.function_table.functions.items():
            if name.startswith(word):
                yield CompletionFunction(function)


class CompletionSymbol(CompletionItem):
    """
    A symbol completion item.
    """

    def __init__(self, symbol):
        self.symbol = symbol

    def to_completion(self, context):
        """
        Returns a LSP representation.
        """
        start = Position(
            line=context.pos.line,
            character=context.pos.char - len(context.word),
        )
        end = Position(
            line=context.pos.line,
            character=context.pos.char,
        )
        return self.completion_build(
            label=self.symbol.name(),
            text_edit=TextEdit(Range(start, end), f'{self.symbol.name()}'),
            detail=f'Symbol. {self.symbol.type()}',
            documentation='TBD',
            completion_kind=CompletionItemKind.Value,
            context=context,
        )


class CompletionFunction(CompletionItem):
    """
    A symbol completion item.
    """

    def __init__(self, function):
        self.function = function

    def to_completion(self, context):
        """
        Returns a LSP representation.
        """
        start = Position(
            line=context.pos.line,
            character=context.pos.char - len(context.word),
        )
        end = Position(
            line=context.pos.line,
            character=context.pos.char,
        )
        name = self.function._name
        return self.completion_build(
            label=name,
            text_edit=TextEdit(Range(start, end), f'{name}()'),
            detail=self.function.pretty(),
            documentation=f'Function: self.function.pretty()',
            completion_kind=CompletionItemKind.Value,
            context=context,
        )
