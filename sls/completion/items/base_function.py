from sls.completion.types import Types
from sls.completion.items.item import CompletionItem


class BaseFunctionCompletionItem(CompletionItem):
    """
    A function completion item.
    """

    def _text_edit(self):
        """
        Include required arguments in the function snippet.
        """
        name = self.insert_name
        text_edit = f"{name}("

        pos = 1
        for arg, sym in self.args().items():
            if pos > 1:
                text_edit += " "
            ty = str(sym.type())
            arg_value = Types.type_insertion(ty, f"${{{pos}:<{ty}>}}")
            text_edit += f"{arg}:{arg_value}"
            pos += 1

        text_edit += ")"
        return text_edit
