from storyscript import loads


class SLSJSONCompiler:
    """
    Allows compiling Storyscript via a LSP request.
    """

    def compile(self, doc, features):
        output = loads(doc.text(), features)
        return {
            "errors": [self.error_to_json(error) for error in output.errors()],
            "deprecations": [
                self.error_to_json(dep) for dep in output.deprecations()
            ],
            "success": output.success(),
            "result": output.result().output() if output.success() else None,
        }

    @staticmethod
    def error_to_json(error):
        """
        Convert an individual error message to JSON.
        """
        error.process()
        return {
            "code": error.error_code(),
            "hint": error.hint(),
            "position": {
                "line": error.int_line(),
                "column": error.start_column(),
                "end_column": error.end_column(),
            },
        }
