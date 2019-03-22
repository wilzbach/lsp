from pytest import mark, raises

from sls.lsp.dispatcher import LSPDispatcher, to_snake_case


@mark.parametrize('method_name,expected', [
    ('MyMethod', 'my_method'),
    ('aMethod', 'a_method'),
])
def test_to_snake_case(method_name, expected):
    assert to_snake_case(method_name) == expected


@mark.parametrize('method_name,expected', [
    ('abc/test', 'rpc_abc__test'),
    ('$/cancelRequest', 'rpc___cancel_request'),
])
def test_dispatcher(method_name, expected):
    class TestClass(LSPDispatcher):
        pass
    test = TestClass()

    # test that the method doesn't exist yet
    with raises(KeyError):
        test[method_name]({'a': 42})

    # add the expected method and test again
    setattr(test, expected, lambda **p: p)
    assert test[method_name]({'a': 42}) == {'a': 42}
