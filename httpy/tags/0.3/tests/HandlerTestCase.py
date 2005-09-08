"""The idea and code for running a test server in another thread are from the
standard library's test/test_socketserver.py.
"""

import os
import select
import socket
import threading
import unittest

from httpy.Config import Config
from httpy.Server import Server


class TestServer(Server):
    """We want to see errors that are raised.
    """

    def handle_error(self, request, client_address):
        self.close_request(request)
        self.server_close()
        raise

class ServerThread(threading.Thread):
    """In order to test the server, we instantiate it in a separate thread.
    """

    def run(self):

        config = {}
        config['mode'] = 'development'
        config['ip'] = ''
        config['root'] = 'root'
        config['port'] = 65370
        config['verbosity'] = 99
        config['apps'] = ''

        server = TestServer(config)
        server.handle_request()

def receive(sock, n, timeout=20):
    """Receive data on our connection with the TestServer.

    It appears that this needs to be at module-level.

    """

    r, w, x = select.select([sock], [], [], timeout)
    if sock in r:
        return sock.recv(n)
    else:
        raise RuntimeError, "timed out on %r" % (sock,)


class HandlerTestCase(unittest.TestCase):

    def setUp(self):

        # [re]build a temporary website tree in ./root
        self.removeTestSite()
        self.buildTestSite()

        self.t = ServerThread()
        self.t.start()

    def send(self, request):
        """This is how we send requests to our TestServer over in its thread.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('localhost', 65370))
        s.sendall(request)
        buf = data = receive(s, 100)
        while data:
            data = receive(s, 100)
            buf += data
        s.close()
        return buf

    def removeTestSite(self):
        if not os.path.isdir('root'):
            return
        for root, dirs, files in os.walk('root', topdown=False):
            for name in dirs:
                os.rmdir(os.path.join(root, name))
            for name in files:
                os.remove(os.path.join(root, name))
        os.rmdir('root')

    def neuter_traceback(self, tb):
        """Given a traceback, return just the system-independent lines.
        """
        tb_list = tb.split(os.linesep)
        if not tb_list[-1]:
            tb_list = tb_list[:-1]
        neutered = []
        for i in range(0,len(tb_list),2):
            neutered.append(tb_list[i])
        neutered.append(tb_list[-1])
        return os.linesep.join(neutered)

    def tearDown(self):
        self.t.join()
        self.removeTestSite()
