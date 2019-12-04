from parso.tree import Leaf, Node


class Stack:
    """
    Utility methods for working with a stack of previous rules.
    """

    @staticmethod
    def extract(stack, value, before=None):
        """
        Returns the respective stack nodes of a rule 'value' seen
        by looking backwards at the stack. An optional 'before' rule
        can be required to be seen first.
        """
        seen = before is None
        for node in reversed(stack):
            from_rule = node.dfa.from_rule
            if not seen:
                if from_rule == before:
                    seen = True
            elif node.dfa.from_rule == value:
                return node.nodes

        assert 0, stack

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

    @staticmethod
    def find_closest_rule(stack, rules):
        """
        Returns the first 'rule' from 'rules' found in the stack.
        """
        for node in reversed(stack):
            from_rule = node.dfa.from_rule
            if from_rule in rules:
                return from_rule

        assert 0, stack

    @staticmethod
    def find_all_until(stack, rule, until, start=0, offset=3):
        """
        Finds all occurrences of a rule until separation 'until' rules are
        reached.
        """
        for node in reversed(stack):
            from_rule = node.dfa.from_rule
            if from_rule == rule:
                for n in node.nodes[start::offset]:
                    arg_name = n.value.lower()
                    yield arg_name
            elif from_rule in until:
                return

        assert 0, stack
