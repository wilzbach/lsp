from sls.completion.scope.items import CompletionBuiltin
from sls.logging import logger

from storyscript import loads
from storyscript.compiler.semantics.functions.MutationTable import (
    MutationTable,
)

from storyscript.compiler.semantics.types.Types import ObjectType

from .property import PropertyCompletionSymbol

log = logger(__name__)


EXPR_TYPE_RESOLVE_DUMMY_VAR = "_sls_expr_resolv_var"


class DotCompletion:
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
        text = f"{EXPR_TYPE_RESOLVE_DUMMY_VAR} = {expr}"
        scope = self.cache.current.current_scope.copy()
        story = loads(text, scope=scope, backend="semantic")
        if not story.success():
            log.debug("DotExprResolvError: %s", story.errors())
            return
        symbol = scope.resolve(EXPR_TYPE_RESOLVE_DUMMY_VAR)
        assert symbol is not None
        return symbol.type()

    def complete(self, expr):
        """
        Perform dot completion for mutation
        """
        log.debug("complete: %s", expr)
        ty = self.expr_type_resolver(expr)
        if ty is None:
            return
        muts = self.mutation_table.resolve_by_type(ty)
        for mut in muts:
            yield CompletionBuiltin(expr, mut.instantiate(ty))

        if isinstance(ty, ObjectType):
            # properties
            for prop_name, prop_value in ty._object.items():
                yield PropertyCompletionSymbol(expr, prop_name, prop_value)
