from sls.logging import logger

from sls.parser.stack import Stack

from .dot import DotCompletion
from .items.mutation_argument import MutationArgument


log = logger(__name__)


class BuiltinCompletion:
    def __init__(self, context_cache):
        self.dot = DotCompletion(context_cache)

    def process_name(self, stack):
        """
        Extract previous token for mutation completion.
        """
        dot_op = self._toks(stack)
        toks = [t.value for t in Stack.flatten(dot_op)]
        # always remove the final dot
        assert toks[-1] == "."
        expr = "".join(toks[:-1])
        yield from self.dot.complete(expr)

    def _toks(self, stack, before=None):
        """
        Returns all tokens from the stack belonging to the current mutation.
        """
        return [
            *Stack.extract(stack, "dot_op", before),
            *Stack.extract(stack, "dot_expr", before),
        ]

    def process_args(self, stack):
        """
        Looks for the mutation name token in the stack and filter seen arguments.
        """
        dot_op = self._toks(stack, before="mut_arguments")
        toks = [t.value for t in Stack.flatten(dot_op)]
        mut_name = toks.pop()
        # remove '.' from mut_name (.<mut_name>)
        expr = "".join(toks[:-1])

        # second or further arguments -> filter used arguments
        prev_args = Stack.find_all_until(
            stack, "mut_arguments", ["dot_expr"], start=1, offset=3
        )
        # '(' (<name> ':' <expr>)*
        prev_args = [*prev_args]

        args = self.args(expr, mut_name, prev_args)

        seen = {}
        for arg in args:
            arg_name = arg.name.lower()
            if arg_name in seen:
                continue
            seen[arg_name] = True
            # ignore previously used args
            if arg_name not in prev_args:
                yield arg

    def args(self, expr, mut_name, prev_args):
        """
        Yields the arguments of the respective mutation if it exists.
        """
        log.debug("mut_args completion: %s", expr)
        muts = [*self.dot.mut_arg_complete(expr, mut_name)]

        # some prev arguments might be invalid, filter them out
        valid_prev_args = [
            arg for arg in prev_args if self.is_valid_arg(muts, arg)
        ]

        for mut in muts:
            # Only consider a mutation if all observed, valid arguments occur in it
            if not self.is_reachable_mut(mut, valid_prev_args):
                continue

            # Yield all arguments of a mutation
            for arg_name, arg_type in mut.args().items():
                yield MutationArgument(arg_name, arg_type)

    def is_valid_arg(self, muts, arg):
        """
        Returns `True` if at least one mutation contains `arg`.
        """
        for mut in muts:
            if arg in mut.args():
                return True

        return False

    def is_reachable_mut(self, mut, prev_args):
        """
        Returns `True` if this mutation contains all already observed , valid arguments.
        """
        mut_args = mut.args()
        for arg in prev_args:
            if arg not in mut_args:
                return False
        return True
