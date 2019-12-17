from sls.document import Range, TextEdit
from sls.logging import logger
from sls.parser.lexer import LexerException
from sls.parser.parso import Parser
from sls.parser.stack import Stack

from .completion.context import CompletionContext
from .completion.service_data import ServiceHandler

log = logger(__name__)


class Indentor:
    """
    Keeps track of the current indentation and allows to add more levels.
    """

    def __init__(self, indent_unit):
        self.indent_unit = indent_unit
        self.indent = ""

    def set_indent(self, indent):
        """
        Set the base level of indentation.
        """
        self.indent = indent

    def add(self):
        """
        Add a level of indentation.
        """
        self.indent += self.indent_unit

    def indentation(self):
        """
        Return the current indentation
        """
        return self.indent


class Indentation:
    """
    Computation of the next indentation for a line.
    """

    def __init__(self, service_registry):
        self.parser = Parser()
        self.service = ServiceHandler(service_registry, None)

    def indent(self, ws, doc, pos, options):
        """
        Returns the indentation for the next line based for the given document
        and position.
        """
        context = CompletionContext(ws=ws, doc=doc, pos=pos)
        line = context.line
        log.info("Line on cursor: %s", line)
        indent = " " * (len(line) - len(line.lstrip()))

        indentor = Indentor(options.get("indent_unit", "  "))
        indentor.set_indent(indent)

        self._indent(context, indentor)

        indentation = indentor.indentation()
        insert_pos = pos
        return {
            "indent": indentation,
            "edits": [
                TextEdit(
                    Range(start=insert_pos, end=insert_pos),
                    new_text=f"\n{indentation}",
                ).dump()
            ],
        }

    def _indent(self, context, indentor):
        try:
            tokens = [*self.parser.tokenize(context.line)]
        except LexerException:
            log.warning(f"Lexing error for line: {context.line}")
            return

        if len(tokens) == 0:
            return

        first_tok = tokens[0].text()

        # special case for partially invalid blocks
        if first_tok == "catch" or first_tok == "else":
            indentor.add()
            return

        # shortcut for start of new blocks
        if (
            first_tok == "try"
            or first_tok == "while"
            or first_tok == "if"
            or first_tok == "foreach"
            or first_tok == "when"
            or first_tok == "function"
        ):
            indentor.add()
            return

        # only look at most at the first two tokens
        tokens = tokens[:2]
        try:
            stack = self.parser.stack_tokens(tokens)
        except NotImplementedError:
            log.warning(f"Invalid line: {context.line}")
            return
        except IndexError:
            log.warning(f"Invalid line: {context.line}")
            return

        transitions = [*self.parser.transitions(stack)]
        for tok, dfa in transitions:
            from_rule = dfa.next_dfa.from_rule
            assert len(dfa.dfa_pushes) > 0
            next_rule = dfa.dfa_pushes[0].from_rule
            if from_rule == "service_suffix" and next_rule == "arglist":
                # service blocks should trigger an indent iff they have events
                if self._service_has_events(stack):
                    indentor.add()
                    return
                return

    def _service_has_events(self, stack):
        """
        Returns `True` if the service has events.
        """
        service_name = Stack.extract(stack, "value")[0].value
        service_command = Stack.extract(stack, "service_op")[0].value

        action = self.service.action(service_name, service_command)
        if action is not None:
            if len(action.events()) > 0:
                return True

        return False
