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

        args = self.args(expr, mut_name)

        # second or further arguments -> filter used arguments
        prev_args = Stack.find_all_until(
            stack, "mut_arguments", ["dot_expr"], start=1, offset=3
        )
        # '(' (<name> ':' <expr>)*
        prev_args = [*prev_args]

        seen = {}
        for arg in args:
            arg_name = arg.name.lower()
            if arg_name in seen:
                continue
            seen[arg_name] = True
            # # ignore previously used args
            if arg_name not in prev_args:
                yield arg

    def args(self, expr, mut_name):
        """
        Yields the arguments of the respective mutation if it exists.
        """
        log.debug("mut_args completion: %s", expr)
        muts = self.dot.mut_arg_complete(expr, mut_name)
        for mut in muts:
            for arg_name, arg_type in mut.args().items():
                yield MutationArgument(arg_name, arg_type)
