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
    "if": "if",
    "else": "else",
    "when": "when",
    "foreach": "foreach",
    "while": "while",
    "function": "function",
    "true": "true",
    "false": "false",
    "null": "null",
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

operator_start = ["+", "-", "*", "/", "%", "<", ">", "!", "=", ")", "]", "}"]

# TODO: fix line/column information
# TODO: peek during loop
# TODO: support comments
# TODO: multi-line strings
# TODO: try/catch


class ErrorCodes:
    regex_no_end = 1
    string_no_end = 2
    name_only_alphanumeric = 3
    number_only_digits = 4
    regex_invalid_flag = 5


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
        self.indent_levels = []
        self.ws = 0
        for t in self.ts_iterate():
            ts = self.ts[self.idx - 1 :]
            if t == "/":
                r = yield from self.regex_tok()
                # TODO: allow ws in regex
                if r:
                    continue
            elif t == '"':
                yield from self.string_tok()
                continue
            elif t.isdigit():
                yield from self.int_tok()
                continue
            elif t == "\n":
                # TODO: handle \r
                yield self.create_token(self.idx - 1, self.idx, "nl")
                yield from self.indent_dedent_tok()
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

        # TODO: add EOF or NL if file without

        assert len(self.indent_levels) >= 0
        for _ in self.indent_levels:
            yield self.create_token(self.idx, self.idx, "dedent")

    def tok_keyword(self, t, ts):
        for keyword, id in keywords.items():
            if ts.startswith(keyword):
                if len(ts) > len(keyword):
                    next_char = ts[len(keyword)]
                    # verify that its a true keyword (e.g. followed by ws,
                    # newline, operators)
                    if not (
                        self.is_white(next_char)
                        or self.is_newline(next_char)
                        or next_char in operator_start
                    ):
                        continue

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
        return Token(id, keyword, self.line, self.column)

    def create_operator(self, op, id):
        return Token(id, op, self.line, self.column)

    def create_token(self, start, end, id):
        text = self.ts[start:end]
        return Token(id, text, self.line, self.column)

    def regex_tok(self):
        # TODO: add escaping
        start = self.idx - 1
        idx = self.idx
        while idx < len(self.ts):
            t = self.ts[idx]
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
                if t == "i" or t == "m" or t == "s":
                    # allow regex flags
                    self.idx = idx + 1
                    yield self.create_token(start, self.idx, "regex")
                    return True

                self.error(
                    ErrorCodes.regex_invalid_flag, f"Regex flag {t} is invalid"
                )

            if self.is_newline(t):
                self.error(ErrorCodes.regex_no_end, "Regex must end with /")

            idx = idx + 1

        return False

    def string_tok(self):
        start = self.idx - 1
        escaped = False
        text = ""
        for t in self.ts_iterate():
            if escaped:
                escaped = False
                text += t
                continue

            if t == '"':
                yield Token("string", text, start + 1, self.idx - 1)
                return
            elif t == "\\":
                # next character is escaped
                escaped = True
            elif t == "\n":
                # single-line string
                self.error(ErrorCodes.string_no_end, 'String must end with "')
            else:
                text += t

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
            elif t == ".":
                id = "float"
            elif t in operator_start:
                break
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
            if self.is_white(t) or self.is_newline(t):
                yield self.create_token(start, self.idx, "name")
                return
            if t.isalnum():
                self.pop()
                continue
            if t == "_" or t == "/" or t == "-":
                self.pop()
                continue

            if (
                t == "[" or t == "(" or t == "." or t == ":"
            ) or t in operator_start:
                yield self.create_token(start, self.idx, "name")
                return

            self.error(
                ErrorCodes.name_only_alphanumeric,
                f"Name can only contain alphanumeric characters, not {t}",
            )

        # EOF reached
        yield self.create_token(start, self.idx, "name")

    def indent_dedent(self, start, ws):
        if self.idx > start:
            if ws == self.ws:
                # current indentation
                pass
            elif ws > self.ws:
                self.indent_levels.append(ws)
                yield self.create_token(start, self.idx, "indent")
            else:
                # jump back to the match indent level
                while True:
                    assert len(self.indent_levels) > 0
                    level = self.indent_levels[-1]
                    if level <= ws:
                        break
                    yield self.create_token(start, self.idx, "dedent")
                    self.indent_levels.pop()
        else:
            for _ in self.indent_levels:
                yield self.create_token(start, self.idx, "dedent")
            self.indent_levels = []
        self.ws = ws

    def indent_dedent_tok(self):
        start = self.idx
        ws = 0
        while not self.is_empty():
            t = self.peek()
            if self.is_white(t):
                ws += 1
                self.pop()
                continue
            yield from self.indent_dedent(start, ws)
            return
        # EOF reached
        yield from self.indent_dedent(start, ws)

    @staticmethod
    def is_white(t):
        return t == " " or t == "\t"

    @staticmethod
    def is_newline(t):
        return t == "\r" or t == "\n"

    def error(self, code, msg):
        raise LexerException(code, msg)
