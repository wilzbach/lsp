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
