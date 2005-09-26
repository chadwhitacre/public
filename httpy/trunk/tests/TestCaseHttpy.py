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


class TestCaseHttpy(unittest.TestCase):

    # unittest.TestCase hooks
    # =======================

    def setUp(self):

        self.scrubenv()
        self.config = Config()

        # [re]build a temporary website tree in ./root
        self.removeTestSite()
        self.buildTestSite()

        if self.server:
            self.t = ServerThread()
            self.t.start()

    def tearDown(self):
        if self.server:
            self.t.join()
        self.removeTestSite()
        self.restoreenv()


    # server support
    # ==============

    server = False # Override to True if you want to start a server

    def send(self, request):
        """Given a raw HTTP request, send it to our server over in its thread.
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


    # environment
    # ===========

    def scrubenv(self):
        save = {}
        for opt in Config.options:
            envvar = 'HTTPY_%s' % opt.upper()
            if os.environ.has_key(envvar):
                save[envvar] = os.environ[envvar]
                del os.environ[envvar]
        self.env = save

    def restoreenv(self):
        for k, v in self.env.items():
            os.environ[k] = v
        self.env = {}


    # test site
    # =========

    def buildTestSite(self):
        """Override me! Build it in root and it will be torn down for you.
        """
        pass

    def removeTestSite(self):
        if os.path.isfile('httpy.conf'):
            os.remove('httpy.conf')
        if not os.path.isdir('root'):
            return
        for root, dirs, files in os.walk('root', topdown=False):
            for name in dirs:
                os.rmdir(os.path.join(root, name))
            for name in files:
                os.remove(os.path.join(root, name))
        os.rmdir('root')


    # utils
    # =====

    @staticmethod
    def neuter_traceback(tb):
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

    @staticmethod
    def dict2tuple(d):
        return tuple(sorted(d.iteritems()))
