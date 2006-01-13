#!/usr/bin/env python
"""This is a client library for SMAP. Some objects are also useful for servers.
"""

import base64
import bz2
import logging
import sha
import socket
import sys
from StringIO import StringIO
from email.Generator import Generator
from email.Message import Message

from Crypto.Cipher import AES



# Logging.
# ========

format = "%(name)-16s %(levelname)-8s %(message)s"
logging.basicConfig( level=logging.DEBUG
                   , format=format
                    )
logger = logging.getLogger('smaplib')



# Exceptions
# ==========

class ClientError(StandardError):
    """
    """

class ServerError(StandardError):
    """
    """

class AlreadyStored(StandardError):
    """
    """

class AlreadyRemoved(StandardError):
    """
    """

class InternalServerError(StandardError):
    """
    """


# Message Manipulators
# ====================

class Wrapper:
    """Losslessly converts a message into something without newlines.
    """

    def wrap(self, msg):
        """Can take either a string or an email.Message.Message.
        """
        if isinstance(msg, basestring):
            msg = msg
        elif isinstance(msg, Message):
            fp = StringIO()
            g = Generator(fp, mangle_from_=False, maxheaderlen=0)
            g.flatten(msg)
            msg = fp.getvalue()
        return base64.b64encode(bz2.compress(msg))

    def unwrap(self, msg):
        return bz2.decompress(base64.b64decode(msg))


class DummyCrypter:
    """Used when we don't have a crypt key.
    """

    def encrypt(self, foo):
        return foo

    def decrypt(self, foo):
        return foo


class Padder:
    """AES encryption requires that input length be evenly divisible by 16.
    """

    def pad(self, msg):
        overage = len(msg) % 16
        if overage > 0:
            padder = '`'
            if msg.endswith(padder):
                padder = '~'
            msg += padder * (16 - overage)
        return msg

    def unpad(self, msg):
        padder = '`'
        if not msg.endswith(padder):
            padder = '~'
        msg = msg.rstrip(padder)
        return msg


class DummyPadder:
    """Used when we don't have a crypt key.
    """

    def pad(self, foo):
        return foo

    def unpad(self, foo):
        return foo



# SMAPConn
# ========

class SMAPConn:
    """Represent a connection to an SMAP server.
    """


    # Connection
    # ==========

    sock = None

    def __init__(self, client_id, crypt_key='', address='/tmp/smapd',
                 sockfam=socket.AF_UNIX):
        """Establish a connection to an SMAP server.
        """

        self.address = address

        try:
            self.sock = socket.socket(sockfam, socket.SOCK_STREAM)
            self.sock.connect(address)
        except socket.error, msg:
            if self.sock:
                self.sock.close()
            self.sock = None
            raise


        # Convert our socket to a file API.
        # =================================

        self.in_ = self.sock.makefile('rb', -1)   # buffered
        self.out = self.sock.makefile('wb', 0)    # unbuffered


        # Authenticate
        # ============

        c, v = self.parse(self.readline())
        assert c == 1
        c, v = self.hit(client_id)
        assert c == 1
        c, v = self.hit(crypt_key)
        assert c in (0, 1)
        if c == 1:
            logger.warn('No encryption in use.')


        # Message Manipulators
        # ====================

        self.wrapper = Wrapper()

        if not crypt_key:
            self.crypter = DummyCrypter()
            self.padder = DummyPadder()
        elif crypt_key.replace('-', '') == client_id:
            raise ClientError("Crypt key can't match client ID.")
        elif len(crypt_key) != 32:
            raise ClientError("Crypt key must be 32 bytes long.")
        else:
            self.crypter = AES.new(crypt_key)
            self.padder = Padder()

        logger.info('connected to %s' % self)


    def __repr__(self):
        return "<smap://%s>" % (self.address)
    __str__ = __repr__



    # Extend base file API to support logging.
    # ========================================

    def read(self, size=-1):
        msg = self.in_.read(size)
        logger.debug("RECV: %s" % msg.rstrip('\n'))
        return msg

    def readline(self, size=-1):
        line = self.in_.readline(size)
        logger.debug("RECV: %s" % line.rstrip('\n'))
        return line

    def write(self, msg):
        logger.debug("SEND: %s" % msg.rstrip('\n'))
        self.out.write(msg)



    # Helpers
    # =======

    def hit(self, msg):
        """Given a one-line message, return a parsed one-line response.

        The message to write may but needn't be terminated by a newline. The
        return value will be a two-tuple, the first element of which will be the
        three-digit response code. The second element will be a tuple containing
        any values returned by the server.

        Any error response from the server (codes in the 500 range) will trigger
        a ServerError here.

        """
        if not msg.endswith('\n'):
            msg += '\n'
        self.write(msg)
        response = self.readline().rstrip('\n')
        c, v = self.parse(response)
        if c in (0, 1):
            return (c, v)
        elif c == 2:
            if v == 'Already stored.':
                raise AlreadyStored
            elif v == 'Already removed.':
                raise AlreadyRemoved
            else:
                raise ServerError(v)
        elif c == 3:
            raise InternalServerError(v)

    def parse(self, msg):
        """Given a one-line response from the server, parse it.
        """
        msg = msg.rstrip('\n')
        code_, value = msg.split(' ', 1)
        return int(code_), value



    # Actual API
    # ==========

    def all(self):
        """Return a list of all message IDs.
        """
        c, v = self.hit('all')
        assert c == 1
        msg_ids = []
        while 1:
            msg_id = self.readline().rstrip('\n')
            if not msg_id:
                break
            msg_ids.append(msg_id)
        return msg_ids


    def find(self, query):
        """Given a query, find messages, returning their ids.
        """

        # Clean up and send the query.
        # ===================================
        # Strip whitespace from the ends of each line, and make sure we start
        # with FIND and end with two newlines.

        query = '\n'.join([l.strip() for l in query.splitlines() if l])
        query = 'find\n%s\n\n' % query
        c, v = self.hit(query)
        assert c == 1


        # Read any message IDs off the wire and return.
        # =============================================

        msg_ids = []
        while 1:
            msg_id = self.readline().rstrip('\n')
            if not msg_id:
                break
            msg_ids.append(msg_id)

        return msg_ids


    def headers(self, msg_id):
        """Given a message ID, retrieve the message's headers.
        """
        c, msg = self.hit('headers %s' % msg_id)
        assert c == 0
        return self.wrapper.unwrap(msg)


    def remove(self, msg_id):
        """Given a message ID, remove the message.
        """
        c, feedback = self.hit('remove %s' % msg_id)
        if c == 1:
            raise AlreadyRemoved
        assert c == 0


    def replace(self, msg_id, msg):
        """Given a message ID and a message, replace the one with the other.
        """

        wrapped = self.wrapper.wrap(msg)
        c, remote_msg_id = self.hit('replace %s %s' % (msg_id, wrapped))

        msg = self.padder.pad(msg)
        msg = self.crypter.encrypt(msg)
        msg_id = sha.new(msg).hexdigest()

        if remote_msg_id == msg_id:
            return remote_msg_id
        else:
            raise ClientError('Message storage failed!')

        assert c == 0


    def retrieve(self, msg_id):
        """Given a message ID, retrieve the message.
        """
        c, msg = self.hit('retrieve %s' % msg_id)
        assert c == 0
        return self.wrapper.unwrap(msg)

    get = retrieve


    def stop(self):
        """
        """
        c, v = self.hit('stop')
        assert c == 0


    def store(self, msg):
        """Given a message, store it.

        Takes a string or an email.Message.Message object. Returns a message ID.

        """

        c, remote_msg_id = self.hit('store %s' % self.wrapper.wrap(msg))

        msg = self.padder.pad(msg)
        msg = self.crypter.encrypt(msg)
        msg_id = sha.new(msg).hexdigest()

        if remote_msg_id == msg_id:
            return remote_msg_id
        else:
            raise ClientError('Message storage failed!')

        assert c == 0



if __name__ == '__main__':
    client_id = '44b9ef48-1f6e-45b7-b3f7-f29b471396e2'
    crypt_key = 'c02ebb50b1ef44b19181096099288fca'
    c = SMAPConn(client_id, crypt_key)
    test = open('test.txt').read()
    try:
        id=c.store(test)
    except AlreadyStored:
        pass
    import code; code.interact(local=locals())
    c.stop()
