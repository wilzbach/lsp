from collections import namedtuple

from cachetools import LRUCache

from sls.completion.items.function import CompletionFunction
from sls.logging import logger

from storyscript import loads
from storyscript.compiler.semantics.functions.FunctionTable import (
    FunctionTable,
)
from storyscript.compiler.semantics.functions.HubMutations import hub
from storyscript.compiler.semantics.symbols.Scope import Scope


log = logger(__name__)

CacheOutput = namedtuple("CacheOutput", ["function_table", "root_scope"])


def cache_compile(text):
    """
    Compile text and return CacheOutput on success.
    """
    output = loads(text, backend="semantic")
    if output.success():
        module = output.result().module()
        return CacheOutput(
            function_table=module.function_table, root_scope=module.root_scope
        )


class GlobalScopeCache:
    """
    Cache for other global blocks which caches global context like
        - FunctionTable
        - SymbolTable
    """

    def __init__(self):
        self.function_table = None
        self.mutation_table = hub.mutations()
        self.global_scope = None
        self.block_cache = LRUCache(1000)

    def update(self, context):
        self.global_scope = self.aggregate_scope_blocks(context)
        self.function_table = self.aggregate_function_blocks(context)

    def other_blocks_compiled(self, context):
        """
        Iterator over all blocks except the current.
        Tries to compile each block, cache it and return a CacheOutput.
        """
        for block in context.other_blocks():
            text = context.doc.lines(block.start, block.end)
            story_text = "\n".join(text)
            if story_text in self.block_cache:
                result = self.block_cache[story_text]
            else:
                result = cache_compile(story_text)
                self.block_cache[story_text] = result

            if result is not None:
                yield result

    def aggregate_scope_blocks(self, context):
        """
        Iterates over all non-current blocks and aggregates
        their symbol table into a combined symbol table.
        """
        scope = Scope.root()
        for block in self.other_blocks_compiled(context):
            scope.insert_scope(block.root_scope)
        return scope

    def aggregate_function_blocks(self, context):
        """
        Iterates over all non-current blocks and aggregates
        their function table into a combined function table.
        """
        fn_table = FunctionTable()
        for block in self.other_blocks_compiled(context):
            fn_table.insert_fn_table(block.function_table)
        return fn_table

    def complete(self, word):
        """
        Complete a word with the global symbol and function table.
        """
        for name, function in self.function_table.functions.items():
            if name.startswith(word):
                yield CompletionFunction(function)

    def function(self, fn_name):
        """
        Returns a matching function or None.
        """
        return self.function_table.functions.get(fn_name, None)
