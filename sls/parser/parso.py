from functools import lru_cache

from parso.grammar import Grammar
from parso.parser import BaseParser
from parso.pgen2.generator import ReservedString


from .lexer import Tokenizer
from .token import StoryTokenSpace

# TODO: this grammar is not a full representation of Storyscript yet
story_grammar = """

file_input: block

blocks: (block NL)+
indented_blocks: INDENT blocks DEDENT

block: if_block | foreach_block | while_block | when_block | try_block | fn_block | statement


if_block: 'if' expression NL indented_blocks ('else if' NL indented_blocks)* ['else' NL indented_blocks]
foreach_block: FOREACH expression as_suffix NL blocks
while_block: 'while' expression NL blocks
when_block: 'when' when_expression NL blocks
try_block: 'try' expression NL indented_blocks ['catch' NL indented_blocks]
fn_block: 'function' fn_name [fn_arguments] ['returns' type]


statement: base_expression | return_stmt | break_stmt | continue_stmt | throw_stmt
return_stmt: 'return' [expression]
break_stmt: 'break'
continue_stmt: 'continue'
throw_stmt: 'throw'

base_expression: expression
expression: binary_op
binary_op: unary_op (binary_tok expression | to_tok type)*
binary_tok: '+' | '-' | '*' | '/' | '%' | '^' | 'and' | 'or' | '<' | '<=' | '==' | '!=' | '>' | '>=' | assign_tok

unary_op: dot_op | unary_tok atom
unary_tok: 'not'

dot_op: atom [dot_expr]
dot_expr: (DOT dot_name [mut_arguments] [path_suffix])+
dot_name: NAME
mut_arguments: LPARENS (mut_arg_name COLON expression)* RPARENS
mut_arg_name: NAME

atom: value | LPARENS expression RPARENS

value: NAME [ fn_suffix | service_suffix [as_suffix] | path_suffix ] | NUMBER | STRING | boolean | NULL | list | map
# | REGEX | TIME
fn_suffix: LPARENS arglist RPARENS
service_suffix: service_op [arglist]
service_op: NAME
path_suffix: ('[' expression ']')+

list: '[' [value (value ',' )] ']'
map: '{' [value COLON (value ',' )] '}'
boolean: 'true' | 'false'

arglist: (arg_name COLON expression)*
arg_name: NAME

fn_name: NAME
fn_arguments: (fn_arg_name COLON type)*
fn_arg_name: NAME
type: 'boolean' | 'int' | 'float' | 'string' | 'regex' | 'time' | 'any' | map_type | list_type
map_type: 'Map' '[' type ',' type ']'
list_type: 'List' '[' type ']'

when_expression: when_service_name when_action
when_action: NAME (when_action_name (when_action_suffix | as_suffix) | as_suffix)
when_action_suffix: (COLON expression when_arglist | when_arglist)  [as_suffix]
when_action_name: NAME
when_service_name: NAME
when_arglist: (arg_name COLON expression)*

as_suffix: AS NAME

to_tok: 'to'
# for simplicity assignments are treated as binary operations
assign_tok: '=' | '+=' | '-=' | '*=' | '/=' | '%='

variable_name: NAME
"""


class StoryGrammar(Grammar):
    _token_namespace = StoryTokenSpace()
    _start_nonterminal = "start"

    def __init__(self, bnf_text):
        super(StoryGrammar, self).__init__(
            bnf_text, tokenizer=None, parser=BaseParser,
        )

    def tokenize(self, text):
        for t in Tokenizer(text).tokenize():
            yield t.to_parso()


@lru_cache(maxsize=1)
def story_grammar_instance():
    """
    Return an instance of a StoryGrammar.
    """
    return StoryGrammar(story_grammar)


class Parser:
    """
    Minimalist grammar parsed using parso.
    """

    def __init__(self):
        self._grammar = story_grammar_instance()

    def tokenize(self, text):
        """
        Tokenize text into individual tokens.
        """
        return self._grammar.tokenize(text)

    def transitions(self, stack, with_non_terminals=True):
        """
        Yields all possible non-terminal transitions.
        """
        for stack_node in reversed(stack):
            for transition, value in stack_node.dfa.transitions.items():
                if not isinstance(transition, ReservedString):
                    # A token type
                    yield transition, value

            if not stack_node.dfa.is_final:
                break

    def operators(self, stack):
        """
        Yields all possible terminals from the current stack position.
        """
        for stack_node in reversed(stack):
            for transition in stack_node.dfa.transitions:
                if isinstance(transition, ReservedString):
                    yield transition.value

            if not stack_node.dfa.is_final:
                break

    def transitions_tokens(self, stack):
        return set(stack._allowed_transition_names_and_token_types())

    def with_special_tok(self, tokens):
        """
        Makes sure to abort the parsing once all tokens have been parsed.
        """
        yield from tokens
        raise EOFError()

    def stack(self, text):
        """
        Feed text into parser and return the parser stack.
        """
        tokens = self.tokenize(text)
        return self.stack_tokens(tokens)

    def stack_tokens(self, tokens):
        """
        Feed tokens into parser and return the parser stack.
        """
        tokens = [*tokens]
        p = BaseParser(self._grammar._pgen_grammar, error_recovery=True)
        tokens = self.with_special_tok(tokens)
        try:
            p.parse(tokens)
        except EOFError:
            return p.stack
