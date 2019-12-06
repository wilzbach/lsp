from sls.completion.items.keyword import KeywordCompletionSymbol

from sls.logging import logger

from sls.parser.lexer import LexerException
from sls.parser.parso import Parser
from sls.parser.stack import Stack
from sls.parser.token import StoryTokenSpace

from .builtin import BuiltinCompletion
from .function import FunctionCompletion
from .service import ServiceCompletion


log = logger(__name__)


class ASTAnalyzer:
    def __init__(self, service_registry, context_cache):
        self.parser = Parser()
        self.service = ServiceCompletion(service_registry)
        self.context_cache = context_cache
        self.builtin = BuiltinCompletion(context_cache)
        self.function = FunctionCompletion(context_cache)

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
            yield from self.service.process_name(stack)
        elif next_rule == "arglist":
            if from_rule == "service_suffix":
                yield from self.service.process_command(stack)
            else:
                assert from_rule == "fn_suffix"
                yield from self.function.process_name(stack)
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
            yield from self.builtin.process_name(stack)
        elif next_rule == "mut_arg_name":
            yield from self.builtin.process_args(stack)
        else:
            assert next_rule == "expression", next_rule
            yield from self.get_name("")

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
            yield from self.service.process_args(stack, prev_args)
        else:
            assert last_rule == "fn_suffix"
            yield from self.function.process_args(stack, prev_args)

    def get_name(self, word):
        """
        Yields all symbols and services starting with 'word'.
        """
        log.debug("get_name: %s", word)
        yield from self.context_cache.complete(word)
        yield from self.service.services(word)
