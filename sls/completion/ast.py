from sls.completion.items.keyword import KeywordCompletionSymbol

from sls.logging import logger

from sls.parser.lexer import LexerException
from sls.parser.parso import Parser
from sls.parser.stack import Stack
from sls.parser.token import StoryTokenSpace

from .dot import DotCompletion
from .service import ServiceCompletion
from .items.function_argument import FunctionArgument
from .items.mutation_argument import MutationArgument


log = logger(__name__)


class ASTAnalyzer:
    def __init__(self, service_registry, context_cache):
        self.parser = Parser()
        self.service = ServiceCompletion(service_registry)
        self.context_cache = context_cache
        self.dot = DotCompletion(context_cache)

    def complete(self, context):
        try:
            yield from self._complete(context)
        except LexerException:
            log.warning(f"Invalid line: {context.line}")
            return

    def _complete(self, context):
        is_space = len(context.line) > 0 and context.line[-1] == " "
        log.debug(f"line: '{context.line}'")
        line = context.line

        tokens = [*self.parser.tokenize(line)]

        like_word = ""
        is_word = len(tokens) > 0 and tokens[-1].text().isalnum()
        if not is_space and is_word:
            # remove word from token stream -> save for completion filter
            like_word = tokens.pop().text()
            # case-insensitive searches
            like_word = like_word.lower()

        log.debug("tokens: %s", tokens)

        try:
            stack = self.parser.stack_tokens(tokens)
        except NotImplementedError:
            log.warning(f"Invalid line: {context.line}")
            return

        transitions = [*self.parser.transitions(stack)]

        # iterate all non-terminals in the transitions and
        # processes upcoming next_rules
        for tok, dfa in transitions:
            completion = self.process_nonterminal(tok, dfa, stack)
            for c in completion:
                c = c.to_completion(context)
                if c["label"].lower().startswith(like_word):
                    yield c

        if not self.state_with_ops(transitions):
            log.debug("state without operator completion.")
            return

        for op in self.process_ops(stack):
            if op.keyword.lower().startswith(like_word):
                yield op

    def process_ops(self, stack):
        """
        Yield all potential alphabetic operators
        """
        # only yield an operator once
        ops = set(self.parser.operators(stack))
        for op in ops:
            # only complete alphabetic operators for now
            if op.isalpha():
                yield KeywordCompletionSymbol(op)

    @staticmethod
    def state_with_ops(transitions):
        """
        Iterate over all non-terminal transitions and check whether operators should be yielded.
        For now, this is a simple blacklist of special rules.
        """
        count = 0

        # ignore operator yielding when only special rules have been observed
        only_special_rules = True
        for tok, dfa in transitions:
            if tok == StoryTokenSpace.RPARENS:
                continue
            if tok == StoryTokenSpace.DOT:
                continue
            if tok == StoryTokenSpace.NL:
                continue
            from_rule = dfa.next_dfa.from_rule
            only_special_rules &= from_rule == "service_suffix"
            count += 1

        # no real transitions
        if count == 0:
            return True

        return not only_special_rules

    def process_nonterminal(self, tok, dfa, stack):
        """
        Forwards processing of the non-terminal to its respective processor.
        """
        log.debug("process non-terminal: %s", tok)
        if tok == StoryTokenSpace.NAME:
            yield from self.process_name(dfa, stack)
        elif tok == StoryTokenSpace.NULL:
            yield KeywordCompletionSymbol("null")
        elif tok == StoryTokenSpace.STRING:
            # no completion for strings
            pass
        elif tok == StoryTokenSpace.LPARENS or tok == StoryTokenSpace.RPARENS:
            pass
        elif tok == StoryTokenSpace.DOT:
            pass
        elif tok == StoryTokenSpace.NL:
            pass
        else:
            # no completion for numbers
            assert tok == StoryTokenSpace.NUMBER, tok

    def process_name(self, dfa, stack):
        """
        Completion for a NAME token can be in different contexts.
        This looks at the current stack and distinguishes.
        """
        from_rule = dfa.next_dfa.from_rule
        assert len(dfa.dfa_pushes) > 0
        next_rule = dfa.dfa_pushes[0].from_rule
        log.debug(
            "process_name, from_rule:%s, next_rule:%s", from_rule, next_rule
        )
        if next_rule == "service_suffix":
            assert from_rule == "value"
            service_name = Stack.extract(stack, "value")[0].value
            yield from self.service.get_service_commands(service_name)
        elif next_rule == "arglist":
            if from_rule == "service_suffix":
                yield from self.process_service(stack)
            else:
                assert from_rule == "fn_suffix"
                yield from self.process_fn(stack)
        elif next_rule == "arg_name":
            yield from self.process_args(stack)
        elif next_rule == "block":
            yield from self.get_name("")
        elif next_rule == "fn_arg_name":
            # no name completion for function args in function declaration
            return
        elif next_rule == "fn_name":
            # no name completion for function names in function declaration
            return
        elif next_rule == "fn_arguments":
            # no name completion for function args in function declaration
            return
        elif next_rule == "dot_name":
            yield from self.process_mut(stack)
        elif next_rule == "mut_arg_name":
            yield from self.process_mut_args(stack)
        else:
            assert next_rule == "expression", next_rule
            yield from self.get_name("")

    def process_service(self, stack):
        """
        Extract previous tokens for service argument completion.
        """
        service_name = Stack.extract(stack, "value")[0].value
        service_command = Stack.extract(stack, "service_op")[0].value
        yield from self.service.get_service_arguments(
            service_name, service_command
        )

    def process_fn(self, stack):
        """
        Extract previous token for function completion.
        """
        fn_name = Stack.extract(stack, "value")[0].value
        yield from self.get_fn_args(fn_name)

    def process_mut(self, stack):
        """
        Extract previous token for mutation completion.
        """
        dot_op = self.get_mut_toks(stack)
        toks = [t.value for t in Stack.flatten(dot_op)]
        # always remove the final dot
        assert toks[-1] == "."
        expr = "".join(toks[:-1])
        yield from self.dot.complete(expr)

    def process_args(self, stack):
        """
        Extract previous token for service or function argument completion
        with at least one previous argument. This looks for seen args
        and filters them out.
        """
        suffixes = ["fn_suffix", "service_suffix"]
        last_rule = Stack.find_closest_rule(stack, suffixes)

        # second or further arguments -> filter used arguments
        # <name> ':' <expr>
        prev_args = [
            *Stack.find_all_until(
                stack, "arglist", suffixes, start=0, offset=3
            )
        ]

        if last_rule == "service_suffix":
            yield from self.process_service_args(stack, prev_args)
        else:
            assert last_rule == "fn_suffix"
            yield from self.process_fn_args(stack, prev_args)

    def process_fn_args(self, stack, prev_args):
        """
        Looks for the function name token in the stack and filter seen arguments.
        """
        fn_name = Stack.extract(stack, "value", "fn_suffix")[0].value
        args = self.get_fn_args(fn_name)
        for arg in args:
            arg_name = arg.name.lower()
            # ignore previously used args
            if arg_name not in prev_args:
                yield arg

    def process_service_args(self, stack, prev_args):
        """
        Looks for the service name and command token in the stack and filter seen arguments.
        """
        service_name = Stack.extract(stack, "value", "service_suffix")[0].value
        service_command = Stack.extract(stack, "service_suffix")[0].value
        args = self.service.get_service_arguments(
            service_name, service_command
        )
        for arg in args:
            arg_name = arg.argument.name().lower()
            # ignore previously used args
            if arg_name not in prev_args:
                yield arg

    def get_mut_toks(self, stack, before=None):
        """
        Returns all tokens from the stack belonging to the current mutation.
        """
        return [
            *Stack.extract(stack, "dot_op", before),
            *Stack.extract(stack, "dot_expr", before),
        ]

    def process_mut_args(self, stack):
        """
        Looks for the mutation name token in the stack and filter seen arguments.
        """
        dot_op = self.get_mut_toks(stack, before="mut_arguments")
        toks = [t.value for t in Stack.flatten(dot_op)]
        mut_name = toks.pop()
        # remove '.' from mut_name (.<mut_name>)
        expr = "".join(toks[:-1])

        args = self.get_mut_args(expr, mut_name)

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

    def get_fn_args(self, fn_name):
        """
        Yields the arguments of the respective function if it exists.
        """
        log.debug("fn_args completion: %s", fn_name)
        fn = self.context_cache.function(fn_name)
        if fn is None:
            return
        for arg_name, arg_type in fn.args().items():
            yield FunctionArgument(arg_name, arg_type)

    def get_mut_args(self, expr, mut_name):
        """
        Yields the arguments of the respective function if it exists.
        """
        log.debug("mut_args completion: %s", expr)
        muts = self.dot.mut_complete(expr, mut_name)
        for mut in muts:
            for arg_name, arg_type in mut.args().items():
                yield MutationArgument(arg_name, arg_type)

    def get_name(self, word):
        """
        Yields all symbols and services starting with 'word'.
        """
        log.debug("get_name: %s", word)
        yield from self.context_cache.complete(word)
        yield from self.service.service_registry.find_services(word)
