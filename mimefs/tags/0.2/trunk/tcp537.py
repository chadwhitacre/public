#!/usr/bin/env python

import Queue
import logging
import os
import signal
import socket
import threading
import time
import traceback


format = "%(name)-16s %(levelname)-8s %(message)s"
logging.basicConfig( level=logging.DEBUG
                   , format=format
                    )
logger = logging.getLogger('TCPServer537')


class TCPServer537:
    """Represents a generic TCP server.

    The server can listen on any type of socket, and requests are handled by a
    pool of worker threads.

    """

    def __init__(self, address='/tmp/smapd', sockfam=socket.AF_UNIX, threads=3):

        # Store our socket info.
        # ======================

        self.address = address
        self.sockfam = sockfam


        # Make sure we can stop.
        # ======================
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)


        # Set up our threading infrastructure.
        # ====================================

        self.DIE = threading.Event()
        self.queue = Queue.Queue()
        self.SHUTDOWN = object()
        self.threads = {}
        self.create_threads(threads)
        self.attach()



    # Blah
    # ====

    def start(self):
        """Start the loop thread and then wait.

        The loop is run in a second thread so that the main thread is free to
        wait for signals.

        """
        self.loop_thread = threading.Thread(target = self.loop)
        logger.debug('starting foreman thread')
        self.loop_thread.start()
        logger.info('started server')
        while 1:
            time.sleep(1000000000)


    def loop(self):
        """
        """
        while not self.DIE.isSet():
            request, client_address = self.socket.accept()
            self.queue.put(request)


    def stop(self, signum, frame):
        """Close down.

        This is a bit complicated. First, we have to signal all of our worker
        threads to shut down. Then we let the loop thread know that we are
        shutting down via the DIE Event. However, the loop thread will currently
        be blocked on a socket, so we need to actually hit the socket from the
        outside in order to unblock it.

        """

        signals = {2:'SIGINT', 15:'SIGTERM'}
        logger.info('caught %s, shutting down' % signals[signum])

        logger.debug('closing worker threads')
        threads = self.threads.values()
        for i in range(len(threads)):
            self.queue.put(self.SHUTDOWN)
        for thread_ in threads:
            thread_.join()

        logger.debug('closing socket')
        self.socket.close()

        logger.debug('closing foreman thread')
        self.DIE.set()
        client = socket.socket(self.sockfam, socket.SOCK_STREAM)
        client.connect(self.address)

        logger.debug('done!')
        raise SystemExit(0)



    # Blah
    # ====

    def create_threads(self, threads):
        """Given an integer, create a pool of threads.
        """
        logger.debug('starting worker threads')
        for i in range(threads):
            thread_ = threading.Thread(target=self._respond, args=(i,))
            self.threads[i] = thread_
            thread_.start()


    def _respond(self, thread_id):
        """Given a thread ID, dispatch to the actual worker.
        """
        while True:
            request = self.queue.get()
            if request is self.SHUTDOWN:
                break
            else:
                incoming = request.makefile('rb')
                outgoing = request.makefile('wb')
                try:
                    try:
                        self.respond(incoming, outgoing)
                    except:
                        logger.error(traceback.format_exc())
                finally:
                    if not outgoing.closed:
                        outgoing.flush()
                    outgoing.close()
                    incoming.close()
                    request.close()


    def attach(self):
        """Set up our socket connection.
        """
        self.socket = socket.socket(self.sockfam, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if self.sockfam == socket.AF_UNIX:
            if os.path.exists(self.address):
                os.unlink(self.address)
                logger.debug("unlinking stale socket")
        self.socket.bind(self.address)
        self.socket.listen(5)


    def respond(self, incoming, outgoing):
        """Takes two file objects.

        Default is to echo. Override this method to do something useful.

        """
        line = incoming.readline()
        outgoing.write(line)




if __name__ == '__main__':
    TCPServer537().start()
