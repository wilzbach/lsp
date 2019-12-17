from sls.completion.items.item import SortGroup
from sls.completion.items.keyword import KeywordCompletionSymbol

from sls.logging import logger

from sls.parser.lexer import LexerException
from sls.parser.parso import Parser
from sls.parser.stack import Stack
from sls.parser.token import StoryTokenSpace

from .builtin import BuiltinCompletion
from .function import FunctionCompletion
from .service import ServiceCompletion
from .service_data import ServiceHandler


log = logger(__name__)


class ParseState:
    """
    Detect and keep information about the current parse state.
    """

    def detect(self, tokens):
        self.in_assignment = any(tok.text() == "=" for tok in tokens)
        self.nestedness = self.detect_nestedness(tokens)

    def detect_nestedness(self, tokens):
        """
        Returns the number of open (positive) or unopened (negative) parenthesis.
        A nestedness of `0` means there are either nor parenthesis or all
        opening parenthesis have been followed by a closing one.
        """
        level = 0
        for tok in tokens:
            if tok.type == StoryTokenSpace.LPARENS:
                level += 1
            elif tok.type == StoryTokenSpace.RPARENS:
                level -= 1
        return level


class ASTAnalyzer:
    def __init__(self, service_registry, context_cache):
        self.parser = Parser()
        self.context_cache = context_cache
        self.builtin = BuiltinCompletion(context_cache)
        self.function = FunctionCompletion(context_cache)
        self.service_handler = ServiceHandler(service_registry, context_cache)
        self.service = ServiceCompletion(self.service_handler)

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
        parse_state = ParseState()
        parse_state.detect(tokens)

        # iterate all non-terminals in the transitions and
        # processes upcoming next_rules
        for tok, dfa in transitions:
            completion = self.process_nonterminal(tok, dfa, stack, parse_state)
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
            if tok == StoryTokenSpace.AS:
                continue
            from_rule = dfa.next_dfa.from_rule
            only_special_rules &= from_rule == "service_suffix"
            count += 1

        # no real transitions
        if count == 0:
            return True

        return not only_special_rules

    def process_nonterminal(self, tok, dfa, stack, parse_state):
        """
        Forwards processing of the non-terminal to its respective processor.
        """
        log.debug("process non-terminal: %s", tok)
        if tok == StoryTokenSpace.NAME:
            yield from self.process_name(dfa, stack, parse_state)
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
        elif tok == StoryTokenSpace.COLON:
            pass
        elif tok == StoryTokenSpace.AS:
            yield from self.process_as(stack, parse_state)
        else:
            # no completion for numbers
            assert tok == StoryTokenSpace.NUMBER, tok

    def process_name(self, dfa, stack, parse_state):
        """
        Completion for a NAME token can be in different contexts.
        This looks at the current stack and distinguishes.
        """
        from_rule = dfa.next_dfa.from_rule
        assert len(dfa.dfa_pushes) > 0
        next_rule = dfa.dfa_pushes[0].from_rule
        log.debug(
            "process_name, from_rule:%s, next_rule:%s", from_rule, next_rule,
        )
        if next_rule == "service_suffix":
            assert from_rule == "value", from_rule
            yield from self.service.process_suffix(
                stack,
                value_stack_name="value",
                in_assignment=parse_state.in_assignment,
            )
        elif next_rule == "arglist":
            yield from self.process_arglist(stack, from_rule)
        elif next_rule == "arg_name":
            yield from self.process_arg_name(stack, from_rule)
        elif next_rule == "block":
            yield from self.get_names()
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
        elif next_rule == "when_expression":
            yield from self.get_service_names()
        elif next_rule == "when_action":
            yield from self.service.process_when_name(stack)
        elif next_rule == "when_action_name":
            yield from self.service.process_when_command(stack)
        elif next_rule == "when_arglist":
            yield from self.process_arglist(stack, from_rule)
        elif next_rule == "when_action_suffix":
            yield from self.process_when(stack)
        else:
            assert next_rule == "expression", next_rule
            yield from self.get_names()

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

    def process_arg_name(self, stack, from_rule):
        if from_rule == "when_arglist":
            yield from self.process_when_args(stack)
        else:
            yield from self.process_args(stack)

    def process_arglist(self, stack, from_rule):
        if from_rule == "service_suffix":
            yield from self.service.process_command(
                stack, value_stack_name="value", command_name="service_op",
            )
        elif from_rule == "fn_suffix":
            yield from self.function.process_name(stack)
        else:
            assert from_rule == "when_action_suffix", from_rule
            yield from self.process_when(stack)

    def process_when(self, stack):
        """
        Process a when statement without args.
        """
        name = Stack.extract(stack, "when_expression")[0].value
        when_action = Stack.extract(stack, "when_action")
        action = when_action[0].value
        prev_args = []
        try:
            event = Stack.extract(stack, "when_action_name")[0].value
        except Exception:
            # COLON (only two names provided, add the third name as argument)
            event = None
            prev_args.append(when_action[1].value)

        yield from self.service.when(name, action, event, prev_args)

    def process_when_args(self, stack):
        """
        Process a when statement with args.
        """
        name = Stack.extract(stack, "when_expression")[0].value
        actions = Stack.extract(stack, "when_action")
        suffix = Stack.extract(stack, "when_action_suffix")
        prev_args = [
            *Stack.find_all_until(
                stack, "when_arglist", ["when_expression"], start=0, offset=3
            )
        ]
        event = None
        assert len(actions) == 2
        action = actions[0].value
        # it might have been the event name or an argument
        if len(suffix) > 0 and suffix[0].value == ":":
            prev_args.append(actions[1].value)
        else:
            event = actions[1].value

        yield from self.service.when(name, action, event, prev_args)

    def process_as(self, stack, parse_state):
        """
        Process an upcoming 'as' rule and decide whether it can occur.
        """
        if parse_state.in_assignment:
            # use of 'as' in an assignment is definitely invalid
            return
        if parse_state.nestedness != 0:
            # use of 'as' inside parenthesis is definitely invalid
            return

        as_keyword = KeywordCompletionSymbol(
            "as", sort_group=SortGroup.ContextKeyword
        )
        suffixes = ["service_op", "service_suffix"]

        try:
            last_rule = Stack.find_closest_rule(stack, suffixes)
            service_name = Stack.extract(stack, "value", "service_suffix")[
                0
            ].value
            service_command = Stack.extract(stack, last_rule)[0].value
        except Exception:
            # attempt to parse service_block failed - must be a when_block or
            # similar
            yield as_keyword
            return

        action = self.service_handler.action(service_name, service_command)
        if action is None:
            return

        # only yield 'as' iff the service can start an event block (=it has
        # events)
        if len(action.events()) > 0:
            yield as_keyword

    def get_names(self):
        """
        Yields all symbols and services.
        """
        log.debug("get_names")
        yield from self.context_cache.complete("")
        yield from self.service_handler.services("")

    def get_service_names(self):
        """
        Yields all available service object symbols and services.
        """
        log.debug("get_service_names")
        yield from self.context_cache.service_objects()
        yield from self.service_handler.services("")
