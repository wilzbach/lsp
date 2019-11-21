from .token import Token


single_operators = {
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
}

keywords = {
    "as": "as_operator",
    "to": "to_operator",
    "and": "and_operator",
    "or": "or_operator",
    "not": "not_operator",
    "return": "return",
    "returns": "returns",
    "when": "when",
    "foreach": "foreach",
    "while": "while",
    "function": "function",
}

operators = {
    "+=": "assign_add",
    "-=": "assign_sub",
    "*=": "assign_mul",
    "/=": "assign_div",
    "%=": "assign_mod",
    "==": "equal",
    "!=": "not_equal",
    "<=": "less_equal",
    ">=": "greater_equal",
    "int": "int_type",
    "float": "float_type",
    "boolean": "boolean_type",
    "string": "string_type",
    "time": "time_type",
    "regex": "regex_type",
    "object": "object_type",
    "any": "any_type",
    "Map": "map_type",
    "List": "list_type",
}

# TODO: fix line/column information
# TODO: peek during loop
# TODO: support comments
# TODO: multi-line strings


class ErrorCodes:
    regex_no_end = 1
    string_no_end = 2
    name_only_alphanumeric = 3
    number_only_digits = 4


class LexerException(Exception):
    """
    An exception which occurred during lexing.
    """

    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code


class Tokenizer:
    """
    Converts a Storyscript stream into a token stream.
    """

    def __init__(self, ts):
        self.ts = ts
        self.idx = 0
        self.line = 0
        self.column = 0

    def peek(self):
        return self.ts[self.idx]

    def next(self, i=1):
        if len(self.ts) > self.idx + i:
            return self.ts[self.idx + i]
        return None

    def pop(self):
        t = self.ts[self.idx]
        self.idx += 1
        if t == "\n":
            self.line += 1
            self.column = 0
        else:
            self.column += 1
        return t

    def is_empty(self):
        return len(self.ts) <= self.idx

    def ts_iterate(self):
        while not self.is_empty():
            yield self.pop()

    def tokenize(self):
        for t in self.ts_iterate():
            ts = self.ts[self.idx - 1 :]
            print("[tokenize]", repr(t))
            if t == "/":
                r = yield from self.regex_tok()
                # TODO: allow ws in regex
                if r:
                    continue
            elif t == '"':
                yield from self.string_tok()
                continue
                continue
            elif t.isdigit():
                yield from self.int_tok()
                continue
            elif t == "\n":
                # TODO: handle \r
                yield self.create_token(self.idx - 1, self.idx, "nl")
                yield from self.indent_tok()
                continue
            elif self.is_white(t):
                continue

            r = yield from self.tok_keyword(t, ts)
            if r:
                continue

            r = yield from self.tok_operator(t, ts)
            if r:
                continue

            if t.isalnum() or t == "_":
                yield from self.name_tok()

            yield from self.tok_operator_single(t, ts)

    def tok_keyword(self, t, ts):
        for keyword, id in keywords.items():
            if ts.startswith(keyword):
                if len(ts) == len(keyword) or self.is_white(ts[len(keyword)]):
                    self.idx += len(keyword) - 1
                    yield self.create_keyword(keyword, id)
                    return True
        return False

    def tok_operator(self, t, ts):
        for op, id in operators.items():
            if ts.startswith(op):
                self.idx += len(op) - 1
                yield self.create_operator(op, id)
                return True
        return False

    def tok_operator_single(self, t, ts):
        op = single_operators.get(t, None)
        if op is not None:
            yield self.create_operator(t, op)
            return True
        return False

    def create_keyword(self, keyword, id):
        print("id", id)
        return Token(id, keyword, self.line, self.column)

    def create_operator(self, op, id):
        return Token(id, op, self.line, self.column)

    def create_token(self, start, end, id):
        text = self.ts[start:end]
        return Token(id, text, self.line, self.column)

    def regex_tok(self):
        # TODO: add escaping + flags
        start = self.idx - 1
        idx = self.idx
        while idx < len(self.ts):
            t = self.ts[idx]
            print("t", t)
            # TODO: error on newline
            if t == "/":
                idx += 1
                if idx >= len(self.ts):
                    self.idx = idx
                    yield self.create_token(start, self.idx, "regex")
                    return True
                t = self.ts[idx]
                if self.is_white(t):
                    self.idx = idx
                    yield self.create_token(start, self.idx, "regex")
                    return True
                # TODO: check for invalid flags
                assert 0

            if self.is_newline(t):
                return False

            idx = idx + 1
        return False

    def string_tok(self):
        # TODO: add escaping
        start = self.idx - 1
        for t in self.ts_iterate():
            # TODO: error on newline
            if t == '"':
                yield self.create_token(start, self.idx, "string")
                return

        # EOF reached
        self.error(ErrorCodes.string_no_end, 'String must end with "')

    def int_tok(self):
        # TODO: support +/-
        # TODO: support floating-point
        start = self.idx - 1
        id = "int"
        while not self.is_empty():
            t = self.peek()
            if self.is_white(t) or self.is_newline(t):
                yield self.create_token(start, self.idx, id)
                return
            if t == ".":
                id = "float"
            elif not t.isdigit():
                self.error(
                    ErrorCodes.number_only_digits,
                    "Numbers can only contain digits",
                )

            self.pop()

        # EOF reached
        yield self.create_token(start, self.idx, id)

    def name_tok(self):
        # TODO: check naming
        start = self.idx - 1
        while not self.is_empty():
            t = self.peek()
            print("name", t)
            if self.is_white(t) or self.is_newline(t):
                yield self.create_token(start, self.idx, "name")
                return
            if t.isalnum():
                self.pop()
                continue
            if t == "_" or t == "/":
                self.pop()
                continue

            if t == "[" or t == "(" or t == ".":
                yield self.create_token(start, self.idx, "name")
                return

            self.error(
                ErrorCodes.name_only_alphanumeric,
                f"Name can only contain alphanumeric characters, not {t}",
            )

        # EOF reached
        yield self.create_token(start, self.idx, "name")

    def indent_tok(self):
        start = self.idx
        while not self.is_empty():
            t = self.peek()
            if self.is_white(t):
                self.pop()
                continue
            if self.idx > start:
                yield self.create_token(start, self.idx, "indent")
            return
        # EOF reached
        if self.idx > start:
            yield self.create_token(start, self.idx, "indent")

    @staticmethod
    def is_white(t):
        return t == " " or t == "\t"

    @staticmethod
    def is_newline(t):
        return t == "\r" or t == "\n"

    def error(self, code, msg):
        raise LexerException(code, msg)
