__author__ = 'Oliver Maskery'


from .. import run_server
import threading
import asyncore
import socket
import time
import json


class Client(asyncore.dispatcher_with_send):

    def __init__(self, listener, target, debug_client):
        asyncore.dispatcher_with_send.__init__(self)

        self.dc = debug_client
        self.target = target
        self.listener = listener
        self.buf = ''

        self.local_server_thread = None

        self.running = True

        networking = self.dc.get_page('networking')
        status = networking.get_section('Status')
        self.status_text = status.get_value('Status', 'string', 'initialising')
        self.last_error = status.get_value('Last Error', 'string', '---')
        self.last_error.set('---')

        self.attempt_connection()

    def should_exit(self):
        return not self.running

    def stop(self):
        self.running = False

    def poll(self):
        asyncore.poll()

    def send_message(self, **values):
        data = "%s\n" % json.dumps(values)
        self.send(data.encode())

    def handle_read(self):
        self.buf += self.recv(2048).decode()
        while True:
            end = self.buf.find("\n")
            if end == -1:
                break

            message = self.buf[:end]
            self.buf = self.buf[end+1:]

            self.listener.handle_message(json.loads(message))

    def attempt_connection(self):
        validated = False

        for x in range(2):
            try:
                self.status_text.set('testing connection to %s' % self.target)
                sock = socket.socket()
                sock.settimeout(5.0)
                print("testing connection...")
                sock.connect((self.target, 20000))
                sock.close()
                validated = True
                break
            except socket.error:
                print("failed to connect")
                if x < 1:
                    self.status_text.set('spinning up local server')
                    self.local_server_thread = self.spin_up_local_server()
                    self.target = 'localhost'
                    time.sleep(0.5)
                else:
                    self.stop()

        if not validated:
            raise Exception("unable to connect to remote server or spin up local server")

        self.status_text.set('establishing connection to %s' % self.target)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((self.target, 20000))

    def spin_up_local_server(self):
        print("spinning up local server")
        thread = threading.Thread(target=run_server.main, name='local_server_thread', kwargs={
            'exit_flag': self
        })
        thread.start()
        return thread

    def handle_connect(self):
        print("connected to", self.target)
        if self.local_server_thread is not None:
            self.status_text.set('connected to %s (spun up local server)' % self.target)
        else:
            self.status_text.set('connected to %s' % self.target)
        self.listener.handle_connected(self.target, (self.local_server_thread is not None))

    def handle_close(self):
        print("disconnected")
        self.stop()
        self.status_text.set('disconnected from %s' % self.target)
        self.close()

    def handle_error(self):
        nil, t, v, tbinfo = asyncore.compact_traceback()

        # sometimes a user repr method will crash.
        try:
            self_repr = repr(self)
        except:
            self_repr = '<__repr__(self) failed for object at %0x>' % id(self)

        error_str = 'uncaptured python exception, closing channel %s (%s:%s %s)' % (
            self_repr, t, v, tbinfo
        )

        print("exception: " + error_str)

        self.handle_close()
        self.last_error.set(error_str)
        self.handle_close()
