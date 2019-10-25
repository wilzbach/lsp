from collections import namedtuple

from sls.logging import logger

log = logger(__name__)

ContextBlock = namedtuple('ContextBlock', ['start', 'end'])


class CompletionContext():
    """
    Holds the reference to all information known about the request.
    """

    def __init__(self, ws, doc, pos):
        self.ws = ws
        self.doc = doc
        self.pos = pos
        self.word = doc.word_on_cursor(pos)
        self.line = doc.line_to_cursor(pos)
        self.blocks = [*self._blocks()]

    def _blocks(self):
        """
        Splits Story lines into individual blocks.
        """
        start = 0
        nr_lines = self.doc.nr_lines()
        skip_empty = -1  # no-skip state
        for i in range(1, nr_lines):
            line = self.doc.line(i)
            empty_line = len(line) == 0

            if not empty_line and line[0] != ' ':
                end = i
                if skip_empty > 0:
                    end -= skip_empty
                yield ContextBlock(start, end=end)
                start = i
                skip_empty = 0
            else:
                # ignore empty lines at the start/end of blocks
                if skip_empty >= 0:
                    if empty_line:
                        skip_empty += 1
                    else:
                        skip_empty = -1

        # ignore empty lines at the end
        for i in range(nr_lines, 0, -1):
            line = self.doc.line(i - 1)
            if len(line) > 0:
                yield ContextBlock(start, end=i)
                return

    def _is_current_block(self, block):
        """
        Checks whether a block is the current one.
        """
        return block.start <= self.pos.line and self.pos.line < block.end

    def current_block(self, until_cursor_line=False):
        """
        Returns the lines of the current block.
        """
        for block in self.blocks:
            if self._is_current_block(block):
                if until_cursor_line:
                    end = self.pos.line + 1
                else:
                    end = block.end
                return self.doc.lines(block.start, end)
        return []

    def lines_until_current_block(self):
        """
        Yields until lines the block.
        """
        for block in self.blocks:
            if self._is_current_block(block):
                return
            yield self.doc.lines(block.start, block.end)

    def other_blocks(self):
        """
        Yields all blocks except the current one.
        """
        for block in self.blocks:
            if not self._is_current_block(block):
                yield block
