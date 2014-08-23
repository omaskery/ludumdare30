__author__ = 'Oliver Maskery'


import asyncore
import socket
import signal


class Server(asyncore.dispatcher):

    def __init__(self, debug_client, settings):
        asyncore.dispatcher.__init__(self)
        self.dc = debug_client
        self.settings = settings

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(('', 20000))
        self.listen(100)

        self.running = False

        default_page = self.dc.get_page('default')

        status = default_page.get_section('Status')
        self.status_string = status.get_value('Status', 'string', 'initialising')
        uuid = status.get_value('UUID', 'string', self.settings['uuid'])
        uuid.set(self.settings['uuid'])  # in case it didn't exist before!

    def handle_accepted(self, sock, address):
        pass

    def handle_kill_signal(self, *ignore):
        self.status_string.set('kill signal received')
        self.running = False

    def run(self):
        self.status_string.set('hooking kill signal')
        signal.signal(signal.SIGINT, self.handle_kill_signal)

        self.status_string.set('entering main process loop')
        self.running = True
        while self.running:
            asyncore.poll()

        self.status_string.set('exiting cleanly')
