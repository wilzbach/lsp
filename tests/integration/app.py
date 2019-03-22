from sls import App
from sls.services.consthub import ConstServiceHub


def test_init(hub):
    """
    Tests that an SLS App gets properly initialized.
    """
    app = App()
    assert app.hub is None


def test_init_hub_path(patch):
    """
    Tests that an SLS App with a Hub Path gets properly initialized.
    """
    patch.object(ConstServiceHub, 'from_json')
    hub_path = '.hub.path.'
    app = App(hub_path=hub_path)
    ConstServiceHub.from_json.assert_called_with(hub_path)
    assert app.hub is ConstServiceHub.from_json()


def test_complete(hub):
    """
    Tests that an SLS App can perform completion.
    """
    app = App()
    result = app.complete('.uri.', 'h')
    del result[0]['documentation']
    del result[0]['detail']
    result = [{
        'label': 'http',
        'kind': 3,
        'textEdit': {
            'range': {
                'start': {'line': 0, 'character': 0},
                'end': {'line': 0, 'character': 1},
            },
            'newText': 'http '}
    }]


def test_complete_with_line(hub):
    """
    Tests that an SLS App can perform completion.
    """
    app = App()
    result = app.complete('.uri.', 'foobar\nh', line=1)
    del result[0]['documentation']
    del result[0]['detail']
    result = [{
        'label': 'http',
        'kind': 3,
        'textEdit': {
            'range': {
                'start': {'line': 0, 'character': 0},
                'end': {'line': 0, 'character': 1},
            },
            'newText': 'http '}
    }]


def test_complete_with_line_column(hub):
    """
    Tests that an SLS App can perform completion.
    """
    app = App()
    result = app.complete('.uri.', 'foobar\nhttp foo', line=1, column=1)
    del result[0]['documentation']
    del result[0]['detail']
    result = [{
        'label': 'http',
        'kind': 3,
        'textEdit': {
            'range': {
                'start': {'line': 0, 'character': 0},
                'end': {'line': 0, 'character': 1},
            },
            'newText': 'http '}
    }]
