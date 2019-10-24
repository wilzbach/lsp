from sls.completion.scope.items import CompletionBuiltin
from sls.logging import logger

from storyscript import loads
from storyscript.compiler.semantics.functions.MutationTable \
    import MutationTable


log = logger(__name__)


EXPR_TYPE_RESOLVE_DUMMY_VAR = '_sls_expr_resolv_var'


class DotCompletion():
    """
    Perform dot-completion.
    """
    def __init__(self, cache):
        self.cache = cache
        self.mutation_table = MutationTable.instance()

    def expr_type_resolver(self, expr):
        """
        Resolves an expr to a type.
        """
        text = f'{EXPR_TYPE_RESOLVE_DUMMY_VAR} = {expr}'
        scope = self.cache.current.current_scope.copy()
        story = loads(text, scope=scope, backend='semantic')
        if not story.success():
            log.debug('DotExprResolvError: %s', story.errors())
            return
        symbol = scope.resolve(EXPR_TYPE_RESOLVE_DUMMY_VAR)
        assert symbol is not None
        return symbol.type()

    def complete(self, context):
        """
        Perform dot completion by extraction the expression before the dot.
        The type of this expression is then extraction and
        queried against the mutation table.
        """
        if '.' not in context.word:
            return

        word, *parts, builtin = context.word.split('.')
        if len(word) == 0:
            return

        expr = '.'.join([word, *parts])
        ty = self.expr_type_resolver(expr)
        if ty is None:
            return
        muts = self.mutation_table.resolve_by_type(ty)
        for mut in muts:
            if mut.name().startswith(builtin):
                yield CompletionBuiltin(word, mut.instantiate(ty))
