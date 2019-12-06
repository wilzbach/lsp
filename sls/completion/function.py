from sls.logging import logger

from sls.parser.stack import Stack

from .items.function_argument import FunctionArgument


log = logger(__name__)


class FunctionCompletion:
    def __init__(self, context_cache):
        self.context_cache = context_cache

    def process_name(self, stack):
        """
        Extract previous token for function completion.
        """
        fn_name = Stack.extract(stack, "value")[0].value
        yield from self.args(fn_name)

    def process_args(self, stack, prev_args):
        """
        Looks for the function name token in the stack and filter seen arguments.
        """
        fn_name = Stack.extract(stack, "value", "fn_suffix")[0].value
        args = self.args(fn_name)
        for arg in args:
            arg_name = arg.name.lower()
            # ignore previously used args
            if arg_name not in prev_args:
                yield arg

    def args(self, fn_name):
        """
        Yields the arguments of the respective function if it exists.
        """
        log.debug("fn_args completion: %s", fn_name)
        fn = self.context_cache.function(fn_name)
        if fn is None:
            return
        for arg_name, arg_type in fn.args().items():
            yield FunctionArgument(arg_name, arg_type)
