from cachetools import LRUCache

from sls.completion.scope.items import CompletionSymbol
from sls.logging import logger

from storyscript import loads
from storyscript.compiler.semantics.symbols.Scope import Scope
from storyscript.parser import Tree


log = logger(__name__)

# name of the dummy variable that gets inserted by SLS
CACHE_DUMMY_VAR = '_sls_dummy_var'


def scope_finder(tree, data):
    """
    Searches for a specific token in the tree and then returns the nearest
    scope in the Tree.
    """
    for c in tree.children:
        if isinstance(c, Tree):
            ret = scope_finder(c, data)
            if ret is not None:
                if isinstance(ret, Scope):
                    # a valid scope was found -> return to top
                    return ret
                return c.scope
        else:
            # element in question found -> start search upwards scope search
            if c.value == data:
                return tree.scope or 0

    return tree.scope


class CurrentScopeCache():
    """
    Cache for the current scope
    """
    def __init__(self, global_):
        self.global_ = global_
        self.scope_cache = LRUCache(100)
        self.current_scope = None

    def update(self, context):
        self.current_scope = self.build_current_scope(context)

    def build_current_scope(self, context):
        """
        Tries to build the current scope and extract its symbol table.
        """
        current_block = context.current_block(until_cursor_line=True)
        if len(current_block) == 0:
            return Scope()

        text = ''
        for block in context.lines_until_current_block():
            text += '\n'.join(block)

        current_block_text = '\n'.join(current_block[:-1])
        key = text + current_block_text

        if key in self.scope_cache:
            return self.scope_cache[key]
        else:
            scope = Scope()
            compiled_scope = self._build_current_scope(current_block_text,
                                                       current_block)
            if compiled_scope is not None:
                for symbol in compiled_scope.symbols():
                    if symbol.name() != CACHE_DUMMY_VAR:
                        scope.insert(symbol)
            self.scope_cache[text] = scope
            return scope

    def _build_current_scope(self, text, block):
        # replace current line with a dummy line
        ws = ' ' * (len(block[-1]) - len(block[-1].lstrip()))
        text += f'\n{ws}{CACHE_DUMMY_VAR} = 0'
        scope = self.global_.global_scope.copy()
        output = loads(text, backend='semantic', scope=scope)
        if output.success():
            tree = output.result().output()
            return scope_finder(tree, CACHE_DUMMY_VAR)
        else:
            log.debug('Current scope build failure: %s', output.errors())

    def complete(self, word):
        """
        Complete a word with the scope's current symbol table.
        """
        for symbol in self.current_scope.symbols():
            if symbol.name().startswith(word):
                yield CompletionSymbol(symbol)
