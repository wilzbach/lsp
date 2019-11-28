class TokenType(object):
    def __init__(self, name, contains_syntax=False):
        self.name = name
        self.contains_syntax = contains_syntax

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.name)


class StoryTokenSpace:
    NAME = TokenType("NAME", True)
    NUMBER = TokenType("NUMBER", True)
    STRING = TokenType("STRING", True)
    REGEX = TokenType("REGEX", True)
    TIME = TokenType("TIME", True)
    OPERATOR = TokenType("OPERATOR", True)
    BOOLEAN_TYPE = TokenType("BOOLEAN_TYPE")
    # TODO: more types
    NULL = TokenType("NULL")
    BOOLEAN = TokenType("BOOLEAN", True)
    NL = TokenType("NL")
    INDENT = TokenType("INDENT")
    DEDENT = TokenType("DEDENT")
    LPARENS = TokenType("LPARENS")
    RPARENS = TokenType("RPARENS")

    OTHER = TokenType("OTHER", True)


class Token:
    """
    Represents an individual Storyscript token.
    """

    def __init__(self, id, text, line, column):
        self._id = id
        self._text = text
        self._line = line
        self._column = column

    def __repr__(self):
        return f"tok({self.id()})"

    def id(self):
        return self._id

    def line(self):
        return self._line

    def column(self):
        return self._column

    def text(self):
        return self._text

    def to_parso(self):
        id_ = self.id()
        if id_ == "name":
            ty = StoryTokenSpace.NAME
        elif id_ == "int":
            ty = StoryTokenSpace.NUMBER
        elif id_ == "float":
            ty = StoryTokenSpace.NUMBER
        elif id_ == "add":
            ty = StoryTokenSpace.OPERATOR
        elif id_ == "nl":
            ty = StoryTokenSpace.NL
        elif id_ == "indent":
            ty = StoryTokenSpace.INDENT
        elif id_ == "dedent":
            ty = StoryTokenSpace.DEDENT
        elif id_ == "lparens":
            ty = StoryTokenSpace.LPARENS
        elif id_ == "rparens":
            ty = StoryTokenSpace.RPARENS
        else:
            ty = StoryTokenSpace.OTHER
            # assert 0, id_
        self.type = ty
        self.value = self.text()
        self.start_pos = self.line(), self.column()
        return self

    def __iter__(self):
        yield self.type
        yield self.value
        yield self.start_pos
        yield "PRE"
