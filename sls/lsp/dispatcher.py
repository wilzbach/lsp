import functools
import re


class LSPDispatcher():
    """
    Dispatches incoming JSON RPCS requests to itself.
    Method names are computed by converting camel case to snake case,
    slashes with double underscores, and removing
    dollar signs. Parameter names are converted to snake case too.
    """

    def __getitem__(self, item):
        method = item.replace('$', '').replace('/', '__')
        method_name = f'rpc_{to_snake_case(method)}'
        if hasattr(self, method_name):
            method = getattr(self, method_name)

            @functools.wraps(method)
            def handler(params):
                params = params or {}
                params = {to_snake_case(k): v for k, v in params.items()}
                return method(**params)

            return handler
        raise KeyError()


first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def to_snake_case(name):
    """
    Converts camel case method names to snake_case
    """
    s1 = re.sub(first_cap_re, r'\1_\2', name)
    return re.sub(all_cap_re, r'\1_\2', s1).lower()
