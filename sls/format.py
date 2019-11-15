from storyscript.Story import Story


class Formatter:
    """
    Pretty-print source code.
    """

    def format(self, ws, doc):
        last_line = doc.nr_lines() - 1
        story = Story(doc.text(), features=None)
        new_story = story.parse(parser=None).format()
        resp = [
            {
                "range": {
                    "start": {"line": 0, "character": 0},
                    "end": {
                        "line": last_line,
                        "character": len(doc.line(last_line)),
                    },
                },
                "newText": new_story,
            }
        ]
        return resp
