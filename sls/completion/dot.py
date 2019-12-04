from collections import defaultdict

from sls.completion.items.builtin import CompletionBuiltin
from sls.logging import logger

from storyscript import loads
from storyscript.compiler.semantics.functions.MutationTable import (
    MutationTable,
)

from storyscript.compiler.semantics.types.Types import ObjectType

from sls.completion.items.property import PropertyCompletionSymbol

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

    def mut_arg_complete(self, expr, mut_name):
        """
        Returns a specific mutation overload set for an expression or None.
        """
        ty = self.expr_type_resolver(expr)
        if ty is None:
            return

        muts = self.mutation_table.resolve(ty, mut_name)
        if muts is None:
            return

        for mut in muts.all():
            yield mut.instantiate(ty)

    def complete(self, expr):
        """
        Perform dot completion for mutations and objects.
        """
        log.debug("complete: %s", expr)
        ty = self.expr_type_resolver(expr)
        if ty is None:
            return

        yield from self.mut_complete(expr, ty)

        if isinstance(ty, ObjectType):
            # properties
            for prop_name, prop_value in ty._object.items():
                yield PropertyCompletionSymbol(expr, prop_name, prop_value)

    def mut_complete(self, expr, ty):
        """
        Perform dot completion for a mutation.
        Group mutations overloads of the same name into one mutation.
        """
        muts = self.mutation_table.resolve_by_type(ty)
        mos = defaultdict(list)
        for mut in muts:
            mos[mut.name()].append(mut.instantiate(ty))

        for name, muts in mos.items():
            yield CompletionBuiltin(expr, name, muts)
