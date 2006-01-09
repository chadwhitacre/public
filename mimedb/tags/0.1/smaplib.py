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

class SMAPError(StandardError):
    """
    """

class AlreadyStored(SMAPError):
    """
    """



# Message Manipulators
# ====================

class Wrapper:
    """Losslessly converts a message into something without newlines.
    """

    def wrap(self, msg):
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
        assert c == 0


        # Message Manipulators
        # ====================

        self.wrapper = Wrapper()

        if not crypt_key:
            self.crypter = DummyCrypter()
            self.padder = DummyPadder()
        elif crypt_key.replace('-', '') == client_id:
            raise SMAPError("Crypt key can't match client ID.")
        elif len(crypt_key) != 32:
            raise SMAPError("Crypt key must be 32 bytes long.")
        else:
            self.crypter = AES.new(crypt_key)
            self.padder = Padder()


    def __repr__(self):
        return "<smap://%s>" % (self._address)
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
        a SMAPError here.

        """
        if not msg.endswith('\n'):
            msg += '\n'
        self.write(msg)
        response = self.readline().rstrip('\n')
        c, v = self.parse(response)
        if unicode(c).startswith('5'):
            raise SMAPError(v)
        else:
            return (c, v)

    def parse(self, msg):
        """Given a one-line response from the server, parse it.
        """
        msg = msg.rstrip('\n')
        code_, value = msg.split(' ', 1)
        if code_ == '2':
            raise SMAPError(value)
        return int(code_), value



    # Actual API
    # ==========

    def FIND(self):
        """
        """
        raise NotImplementedError


    def HDRS(self):
        """
        """
        raise NotImplementedError


    def RTRV(self, msg_id):
        """Given a message ID, ReTRieVe a message.
        """
        c, msg = self.hit('RTRV %s' % msg_id)
        assert c == 0
        return self.wrapper.unwrap(msg)


    def STOP(self):
        """
        """
        self.write('STOP\n')


    def STOR(self, msg):
        """Given a message, STORe it.

        Takes a string or an email.Message.Message object. Returns a message ID.

        """

        # Flatten a possible Message object.
        # ==================================

        if isinstance(msg, basestring):
            msg = msg
        elif isinstance(msg, Message):
            fp = StringIO()
            g = Generator(fp, mangle_from_=False, maxheaderlen=0)
            g.flatten(msg)
            msg = fp.getvalue()


        # Store it and verify the hash.
        # =============================

        c, remote_msg_id = self.hit('STOR %s' % self.wrapper.wrap(msg))

        msg = self.padder.pad(msg)
        msg = self.crypter.encrypt(msg)
        msg_id = sha.new(msg).hexdigest()

        if remote_msg_id == msg_id:
            return remote_msg_id
        else:
            raise SMAPError('Message storage failed! (client)')


        # Decide how to respond.
        # ======================

        if c == 1:
            raise AlreadyStored
        assert c == 0


    # Aliases
    # =======

    find = FIND
    headers = hdrs = HDRS
    retrieve = rtrv = RTRV
    store = stor = STOR
    stop = STOP



if __name__ == '__main__':
    client_id = '44b9ef48-1f6e-45b7-b3f7-f29b471396e2'
    crypt_key = 'c02ebb50b1ef44b19181096099288fca'
    c = SMAPConn(client_id, crypt_key)
    import code; code.interact(local=locals())
