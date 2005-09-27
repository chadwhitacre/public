"""The idea and code for running a test._server in another thread are from the
standard library's test/test_socke._server.py.

TODO: This is out of date now that we are using asyncore (via httpy._zope._server).

"""

import asyncore
import os
import select
import socket
import threading
import time
import unittest

from httpy._zope.server.taskthreads import ThreadedTaskDispatcher
from httpy._zope.server.tests.asyncerror import AsyncoreErrorHook

from httpy.Config import ServerConfig
from httpy.Server import Server


td = ThreadedTaskDispatcher()


opts = [ '--mode', 'development'
       , '--ip', ''
       , '--root', 'root'
       , '--port', '65370'
       , '--verbosity', '99'
       #, '--apps', '/' discover automatically
        ]


class TestCaseHttpy(unittest.TestCase, AsyncoreErrorHook):

    # unittest.TestCase hooks
    # =======================

    want_config = False

    def setUp(self):

        self.scrubenv()

        # [re]build a temporary website tree in ./root
        self.removeTestSite()
        self.buildTestSite()

        if self.server:
            self.startServer()

        if self.want_config:
            self.config = ServerConfig()



    def tearDown(self):
        if self.server:
            self.stopServer()
        self.removeTestSite()
        self.restoreenv()


    # server support
    # ==============

    server = False # Override to True if your subclass needs a server

    def startServer(self):
        if len(asyncore.socket_map) != 1:
            # Let sockets die off.
            # TODO tests should be more careful to clear the socket map.
            asyncore.poll(0.1)
        self.orig_map_size = len(asyncore.socket_map)
        #self.hook_asyncore_error()
        config = ServerConfig(opts)
        self._server = Server(config, threads=4)
        self._server.accept_connections()
        self.port = self._server.socket.getsockname()[1]
        self.run_loop = 1
        self.counter = 0
        self.thread_started = threading.Event()
        self.thread = threading.Thread(target=self.loop)
        self.thread.setDaemon(True)
        self.thread.start()
        self.thread_started.wait(10.0)
        self.assert_(self.thread_started.isSet())

    def stopServer(self):
        self.run_loop = 0
        self.thread.join()
        td.shutdown()
        self._server.close()
        # Make sure all sockets get closed by asyncore normally.
        timeout = time.time() + 5
        while 1:
            if len(asyncore.socket_map) == self.orig_map_size:
                # Clean!
                break
            if time.time() >= timeout:
                self.fail('Leaked a socket: %s' % `asyncore.socket_map`)
            asyncore.poll(0.1)
        #self.unhook_asyncore_error()

    def loop(self):
        self.thread_started.set()
        while self.run_loop:
            self.counter = self.counter + 1
            asyncore.poll(0.1)


    # environment
    # ===========

    def scrubenv(self):
        save = {}
        for opt in ServerConfig.options:
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
        os.mkdir('root')

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
