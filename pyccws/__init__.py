
import pychromecast
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
import json
import logging

logger = logging.getLogger(__name__)

class Client(WebSocketApplication):
    def __init__(self, ws, chromecast_wrapper):
        WebSocketApplication.__init__(self, ws)
        self.chromecast_wrapper = chromecast_wrapper
        logger.debug('Client created')

    def send(self, message):
        self.ws.send(message)

    def on_open(self):
        logger.debug('Socket opened')
        self.chromecast_wrapper.on_open(self)

    def on_message(self, message):
        if message is None:
            return
        self.chromecast_wrapper.on_message(message, self)

    def on_close(self, reason):
        logger.debug('Socket closed')
        self.chromecast_wrapper.on_close(self)

class ClientHandler(object):
    def __init__(self, chromecast_wrapper):
        self.chromecast_wrapper = chromecast_wrapper

    def __call__(self, ws):
        return Client(ws, self.chromecast_wrapper)

class PyCCWS(object):
    def __init__(self):
        self.client_handler = ClientHandler(self)
        self.clients = []
        self.chromecast = None

    def connect_to_chromecast(self, friendly_name):
        self.chromecast = pychromecast.get_chromecast(friendly_name = friendly_name)
        logger.debug('Connected to Chromecast: %s' % self.chromecast)

        self.chromecast.socket_client.receiver_controller.register_status_listener(self)
        self.chromecast.socket_client.media_controller.register_status_listener(self)

    def listen(self, port, host = ''):
        server = WebSocketServer((host, port), Resource({'/': self.client_handler}))
        logger.debug('server will listening on %d %s' % (port, server))
        server.serve_forever()

    def send(self, message):
        logger.debug('send message to %d clients' % len(self.clients))
        for client in self.clients:
            client.send(message)

    def on_open(self, client):
        logger.debug('add client %s' % client)
        self.clients.append(client)

    def on_message(self, message, client):
        if self.chromecast is None:
            return
        self.cast.send(message)

    def on_close(self, client):
        logger.debug('remove clients [%d]' % self.clients.index(client))
        self.clients.remove(client)

    def new_cast_status(self, status):
        msg = json.dumps(dict(type = 'new_cast_status', data = status.__dict__))
        logger.debug("new status: " + msg)
        self.send(msg)

    def new_media_status(self, status):
        msg = json.dumps(dict(type = 'new_media_status', data = status.__dict__))
        logger.debug("new status: " + msg)
        self.send(msg)
