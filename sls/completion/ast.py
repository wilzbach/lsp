from .keyword import KeywordCompletionSymbol

from sls.logging import logger
from sls.services.action import Action
from sls.services.argument import Argument
from sls.services.function_argument import FunctionArgument

from sls.parser.lexer import LexerException
from sls.parser.parso import Parser
from sls.parser.token import StoryTokenSpace


log = logger(__name__)


class ASTAnalyzer:
    def __init__(self, service_registry, context_cache):
        self.parser = Parser()
        self.service_registry = service_registry
        self.context_cache = context_cache

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
        if "." in context.word:
            # handled by DotCompletion
            return

        tokens = [*self.parser.tokenize(line)]

        like_word = ""
        is_word = len(tokens) > 0 and tokens[-1].text().isalnum()
        if not is_space and is_word:
            # remove word from token stream -> save for completion filter
            like_word = tokens.pop().text()
            # case-insensitive searches
            like_word = like_word.lower()

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

    def state_with_ops(self, transitions):
        """
        Iterate over all non-terminal transitions and check whether operators should be yielded.
        For now, this is a simple blacklist of special rules.
        """
        if len(transitions) == 0:
            return True

        # ignore operator yielding when only special rules have been observed
        only_special_rules = True
        for tok, dfa in transitions:
            if tok == StoryTokenSpace.RPARENS:
                continue
            from_rule = dfa.next_dfa.from_rule
            only_special_rules &= from_rule == "service_suffix"

        return not only_special_rules

    def process_nonterminal(self, tok, dfa, stack):
        """
        Forwards processing of the non-terminal to its respective processor.
        """
        if tok == StoryTokenSpace.NAME:
            yield from self.process_name(dfa, stack)
        elif tok == StoryTokenSpace.NULL:
            yield KeywordCompletionSymbol("null")
        elif tok == StoryTokenSpace.STRING:
            # no completion for strings
            pass
        elif tok == StoryTokenSpace.LPARENS or tok == StoryTokenSpace.RPARENS:
            pass
        else:
            # no completion for numbers
            assert tok == StoryTokenSpace.NUMBER, tok

    @staticmethod
    def extract(stack, value, before=None):
        """
        Returns the respective stack nodes of a rule 'value' seen
        by looking backwards at the stack. An optional 'before' rule
        can be required to be seen first.
        """
        seen = before is None
        for node in reversed(stack):
            from_rule = node.dfa.from_rule
            if not seen:
                if from_rule == before:
                    seen = True
            elif node.dfa.from_rule == value:
                return node.nodes

        assert 0, stack

    def process_name(self, dfa, stack):
        """
        Completion for a NAME token can be in different contexts.
        This looks at the current stack and distinguishes.
        """
        from_rule = dfa.next_dfa.from_rule
        assert len(dfa.dfa_pushes) > 0
        next_rule = dfa.dfa_pushes[0].from_rule
        if next_rule == "service_suffix":
            assert from_rule == "value"
            service_name = self.extract(stack, "value")[0].value
            yield from self.get_service_commands(service_name)
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
        else:
            assert next_rule == "expression", next_rule
            yield from self.get_name("")

    def process_service(self, stack):
        """
        Extract previous tokens for service argument completion.
        """
        service_name = self.extract(stack, "value")[0].value
        service_command = self.extract(stack, "service_op")[0].value
        yield from self.get_service_arguments(service_name, service_command)

    def process_fn(self, stack):
        """
        Extract previous token for function completion.
        """
        fn_name = self.extract(stack, "value")[0].value
        yield from self.get_fn_args(fn_name)

    @staticmethod
    def stack_find_closest_rule(stack, rules):
        """
        Returns the first 'rule' from 'rules' found in the stack.
        """
        for node in reversed(stack):
            from_rule = node.dfa.from_rule
            if from_rule in rules:
                return from_rule

        assert 0, stack

    @staticmethod
    def stack_find_all_until(stack, rule, until):
        """
        Finds all occurences of a rule until separation 'until' rules are
        reached.
        """
        for node in reversed(stack):
            from_rule = node.dfa.from_rule
            if from_rule == rule:
                # <name> ':' <expr>
                for node in node.nodes[::3]:
                    arg_name = node.value.lower()
                    yield arg_name
            elif from_rule in until:
                return

        assert 0, stack

    def process_args(self, stack):
        """
        Extract previous token for service or function argument completion
        with at least one previous argument. This looks for and filters
        seen arguments.
        """
        suffixes = ["fn_suffix", "service_suffix"]
        last_rule = self.stack_find_closest_rule(stack, suffixes)

        # second or further arguments -> filter used arguments
        prev_args = self.stack_find_all_until(stack, "arglist", suffixes)

        if last_rule == "service_suffix":
            yield from self.process_service_args(stack, prev_args)
        else:
            assert last_rule == "fn_suffix"
            yield from self.process_fn_args(stack, prev_args)

    def process_fn_args(self, stack, prev_args):
        """
        Looks for the function name token in the stack and filter seen arguments.
        """
        fn_name = self.extract(stack, "value", "fn_suffix")[0].value
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
        service_name = self.extract(stack, "value", "service_suffix")[0].value
        service_command = self.extract(stack, "service_suffix")[0].value
        args = self.get_service_arguments(service_name, service_command)
        for arg in args:
            arg_name = arg.argument.name().lower()
            # ignore previously used args
            if arg_name not in prev_args:
                yield arg

    def get_fn_args(self, fn_name):
        """
        Yields the arguments of the respective function if it exists.
        """
        log.debug("function_name completion: %s", fn_name)
        fn = self.context_cache.function(fn_name)
        if fn is None:
            return
        for arg_name, arg_type in fn.args().items():
            yield FunctionArgument(arg_name, arg_type)

    def get_service_commands(self, service_name):
        """
        Yields the commands of the respective service if it exists.
        """
        log.debug("get_service_commands: %s", service_name)
        service = self.service_registry.get_service_data(service_name)
        if service is None:
            return

        service_config = service.configuration()
        for action in service_config.actions():
            yield Action(action)

    def get_service_arguments(self, service_name, command_name):
        """
        Yields the arguments of the respective service command if it exists.
        """
        log.debug("get_service_arguments: %s %s", service_name, command_name)
        service = self.service_registry.get_service_data(service_name)
        if service is None:
            return

        service_config = service.configuration()

        command = service_config.command(command_name)
        if command is not None:
            for arg in command.args():
                yield Argument(arg)

        action = service_config.action(command_name)
        if action is not None:
            for arg in action.args():
                yield Argument(arg)

    def get_name(self, word):
        """
        Yields all symbols and services starting with 'word'.
        """
        log.debug("get_name: %s", word)
        yield from self.context_cache.complete(word)
        yield from self.service_registry.find_services(word)
