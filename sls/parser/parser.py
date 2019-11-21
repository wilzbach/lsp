class Parser:
    """
    Small Storyscript parser.
    """

    def __init__(self, ts):
        self.ts = ts

    def current(self):
        return self.ts.current

    def start(self):
        if self.current().name == "when":
            self.parse_when()

    def parse_when():
        pass

    def parse_foreach():
        pass

    def parse_while():
        pass

    def parse_expression():
        pass

    def parse_function():
        pass

    def parse_service_call():
        pass
