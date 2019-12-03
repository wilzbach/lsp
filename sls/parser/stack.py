from parso.tree import Leaf, Node


class Stack:
    """
    Utility methods for working with a stack of previous rules.
    """

    @staticmethod
    def flatten(stack):
        """
        Reduces a tree stack into a flat list of all leafs.
        """
        if isinstance(stack, Leaf):
            yield stack
            return

        if isinstance(stack, Node):
            stack = stack.children
        for node in stack:
            yield from Stack.flatten(node)
