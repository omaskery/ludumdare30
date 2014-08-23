__author__ = 'Oliver Maskery'


from .. import common
import asyncore
import socket
import random
import json


class Server(asyncore.dispatcher):

    def __init__(self, debug_client, settings, exit_flag):
        asyncore.dispatcher.__init__(self)
        self.dc = debug_client
        self.settings = settings
        self.exit_flag = exit_flag

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(('', 20000))
        self.listen(100)

        default_page = self.dc.get_page('default')

        self.world = common.World(debug_client)
        self.clients = []

        self.world.generate(100)

        status = default_page.get_section('Status')
        self.status_string = status.get_value('Status', 'string', 'initialising')
        uuid = status.get_value('UUID', 'string', self.settings['uuid'])
        uuid.set(self.settings['uuid'])  # in case it already exists
        self.connections = status.get_value('Connections', 'int', 0)
        self.connections.set(0)  # in case it already exists

    def handle_accepted(self, sock, address):
        client = Connection(self, sock, address)
        self.clients.append(client)
        self.connections.set(len(self.clients))

    def remove(self, client):
        self.clients.remove(client)
        self.connections.set(len(self.clients))

    def run(self):
        self.status_string.set('running main process loop')
        while not self.exit_flag.should_exit():
            asyncore.poll()

        self.status_string.set('exiting cleanly')


class Connection(asyncore.dispatcher_with_send):

    def __init__(self, server, sock, address):
        asyncore.dispatcher_with_send.__init__(self, sock)
        self.address = address
        self.server = server
        self.buf = ''

        self.player = None
        self.node = None

        self.handlers = {
            'connect': self.handle_msg_connect
        }

        print("[%s] connected" % self.address[0])

        self.send_message(message='welcome to the server!')

    def handle_read(self):
        self.buf += self.recv(2048).decode()
        while True:
            end = self.buf.find("\n")
            if end == -1:
                break

            message = self.buf[:end]
            self.buf = self.buf[end+1:]

            self.handle_message(json.loads(message))

    def handle_message(self, message):
        print("[%s] %s" % (self.address[0], message))

        if 'cmd' not in message.keys():
            return

        if message['cmd'] not in self.handlers.keys():
            return

        self.handlers[message['cmd']](message)

    def handle_msg_connect(self, message):
        self.player = common.Player()
        self.player.unblob(message['player'])

        print("player connect message received: " + " ".join(self.player.name))

        self.node = random.choice(self.server.world.nodes)
        self.node.entities.append(self.player)

        self.player.pos = self.node.random_free_position(self.node.random_position, True)

        self.send_message(ack='connect', success=True, pos=self.player.pos)

    def send_message(self, **values):
        data = "%s\n" % json.dumps(values)
        self.send(data.encode())

    def handle_close(self):
        print("[%s] disconnecting" % self.address[0])
        self.server.remove(self)
        self.close()
