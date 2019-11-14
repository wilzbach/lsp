import json

import tornado
import tornado.web
import tornado.websocket

from ..logging import logger

log = logger(__name__)


def sls_websocket(sls_app):
    class SLSWebSocketHandler(tornado.websocket.WebSocketHandler):
        def check_origin(self, origin):
            return True

        def open(self):
            self._ls = sls_app.language_server(hub=sls_app.hub)
            self._ls.set_endpoint(self.write_object)

        def on_message(self, message):
            try:
                self._ls.endpoint.consume(json.loads(message))
            except ValueError:
                log.exception('Failed to parse JSON message %s', message)

        def write_object(self, obj):
            self.write_message(json.dumps(obj))

        def on_close(self):
            log.warn('WebSocket closed')

    return SLSWebSocketHandler


class SLSApplication(tornado.web.Application):
    def __init__(self, sls_app):
        handlers = [(r'/', sls_websocket(sls_app))]
        super(SLSApplication, self).__init__(handlers)
