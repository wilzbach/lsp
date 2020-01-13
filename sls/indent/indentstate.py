class IndentState:
    """
    Keeps track of the current indentation and allows to add more levels.
    """

    def __init__(self, indent_unit):
        self.indent_unit = indent_unit
        self.indent = ""

    def add(self):
        """
        Add a level of indentation.
        """
        self.indent += self.indent_unit
        return self

    def indentation(self):
        """
        Return the current indentation
        """
        return self.indent

    @classmethod
    def detect(cls, line, indent_unit):
        """
        Detect the indentation of the current line and return an
        indent_state instance of it.
        """
        indent_state = cls(indent_unit)
        indent_state.indent = " " * (len(line) - len(line.lstrip()))
        return indent_state
