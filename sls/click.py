from sls.completion.ast import ASTAnalyzer
from sls.completion.cache import ContextCache
from sls.completion.context import CompletionContext
from sls.logging import logger
from sls.parser.parso import Parser

log = logger(__name__)

operators = {
    "+": "add",
    "-": "sub",
    "*": "mul",
    "/": "div",
    "^": "pow",
    "%": "mod",
    "(": "lparens",
    ")": "rparens",
    "[": "lbracket",
    "]": "rbracket",
    "{": "lcurly",
    "}": "rcurly",
    ":": "colon",
    ".": "dot",
    ",": "comma",
    "=": "assign",
    "<": "less",
    ">": "greater",
    "+=": "assign_add",
    "-=": "assign_sub",
    "*=": "assign_mul",
    "/=": "assign_div",
    "%=": "assign_mod",
    "==": "equal",
    "!=": "not_equal",
    "<=": "less_equal",
    ">=": "greater_equal",
}


class Click:
    def __init__(self, service_registry):
        self.parser = Parser()
        self.context_cache = ContextCache(
            service_registry.hub, until_cursor_line=False
        )
        self.ast = ASTAnalyzer(service_registry, self.context_cache)
        self.plugins = [
            self.tokens,
            self.operator,
            self.test_completion,
        ]

    def click(self, ws, doc, pos):
        context = CompletionContext(ws=ws, doc=doc, pos=pos)
        log.info(
            "Word on cursor: %s (full: %s)", context.word, context.full_word()
        )
        tokens = [*self.parser.tokenize(context.line)]
        self.context_cache.update(context)
        for plugin in self.plugins:
            res = plugin(context, tokens)
            if res is not None:
                return res

        return {"detail": "UNKNOWN"}

    def test_completion(self, context, tokens):
        word = context.full_word()
        completion = self.gather_completion(context)
        for item in completion:
            if item["label"] == word:
                del item["textEdit"]
                del item["sortText"]
                del item["documentation"]
                del item["insertTextFormat"]
                return item

    def tokens(self, context, tokens):
        if len(tokens) == 0:
            return

        tok = tokens[-1]
        tok_id = tok.id()
        if tok_id == "int":
            return {"detail": f"Token {tok.id()} {tok.text()}"}
        if tok_id == "string":
            return {"detail": f"Token {tok.id()} {tok.text()}"}
        if tok_id == "regex":
            return {"detail": f"Token {tok.id()} {tok.text()}"}

    def gather_completion(self, context):
        ret = self.ast.complete(context)
        # serialize all items
        for item in ret:
            # check whether serialization is necessary
            if isinstance(item, dict):
                yield item
            else:
                yield item.to_completion(context)

    def operator(self, context, tokens):
        word = context.full_word()
        if word in operators:
            return {"detail": f"Operator {word}"}
