#!/usr/bin/env python

import anydbm
import base64
import bz2
import codecs
import logging
import os
import sets
import sha
import traceback
from email import message_from_file, message_from_string

from Crypto.Cipher import AES

import smaplib
from tcp537 import TCPServer537



logger = logging.getLogger('smapd')
ROOT = '/var/db/smap/'
CLIENT_IDS = os.listdir(ROOT)
ALLOWED = ( 'all'
          , 'find'
          , 'headers'
          , 'remove'
          , 'replace'
          , 'retrieve'
          , 'stop'
          , 'store'
           )


class Done(StandardError):
    """Signal for the end of a conversation
    """

class SendLine(StandardError):
    """Signal for the end of a request.
    """



class Conversation:
    """Represents a persistent connection.
    """

    client_id = ''
    crypter = None
    padder = None
    wrapper = smaplib.Wrapper()

    def __init__(self, incoming, outgoing):
        self.in_ = incoming
        self.out = outgoing


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

    def write(self, msg=''):
        if not msg.endswith('\n'):
            msg += '\n'
        logger.debug("SEND: %s" % msg.rstrip('\n'))
        self.out.write(msg)
        self.out.flush()
        if msg.split()[0:1] == ['2']:
            raise SendLine



    # Main Loop
    # =========

    def have(self):
        """Have a conversation. Get it? Get it?
        """

        self.client_id = self.get_client_id()
        self.crypter = self.get_crypter()

        while 1:
            try:
                request = self.readline().rstrip()
                tokens = request.split()
                command = tokens[0].lower()
                args = tokens[1:]
                if command not in ALLOWED:
                    self.write('2 Bad request.')
                method = getattr(self, command)
                method(*args)
            except SendLine:
                pass


    def get_client_id(self):
        """Return the client ID to use for this conversation.
        """

        self.write('1 SMAP/0.2 Welcome! Your client ID?')
        client_id = ''
        while not client_id:
            try:
                client_id = self.readline().rstrip('\n')
                if client_id in CLIENT_IDS:
                    self.data_root = os.path.join(ROOT, client_id, 'data')
                    self.metadata_root = os.path.join(ROOT, client_id, 'metadata')
                    self.write('1 Thanks! Your crypt key? (optional)')
                else:
                    self.write('2 Bad client ID; try again.')
            except SendLine:
                pass

        return client_id


    def get_crypter(self):
        """Return the crypter object to use for this conversation.
        """

        crypter = None
        while not crypter:
            try:
                crypt_key = self.readline().rstrip('\n')

                if not crypt_key:
                    crypter = smaplib.DummyCrypter()
                    self.padder = smaplib.DummyPadder()
                    self.write('1 Ok, your data will be stored unencrypted.')
                elif crypt_key.replace('-', '') == self.client_id:
                    self.write("2 Crypt key can't match client ID.")
                elif len(crypt_key) != 32:
                    self.write("2 Crypt key must be 32 bytes long.")
                else:
                    crypter = AES.new(crypt_key)
                    self.padder = smaplib.Padder()
                    self.write('0 You have chosen ... wisely!')
            except SendLine:
                pass

        return crypter


    # Actual API
    # ==========

    def all(self):
        """Return a list of all message IDs.
        """
        msg_ids = os.listdir(self.data_root)
        self.write('1 Message IDs follow.')
        for msg_id in msg_ids:
            self.write(msg_id)
        self.write()


    def find(self):
        """Find messages, returning their IDs.
        """

        # Gather and validate all criteria.
        # =================================
        # header = value\nheader2 < value2\n header2 >= value3\n\n

        criteria = []
        err_msg = ''
        while 1:
            criterion = self.readline().rstrip('\n')
            if not criterion:
                break
            elif err_msg:
                continue
            else:
                tokens = criterion.split(None, 2)
                if len(tokens) != 3:
                    err_msg = 'Bad criterion (too few tokens): %s' % criterion
                elif tokens[1] not in ('>', '>=', '=', '!=', '<=', '<'):
                    err_msg = 'Bad criterion (bad operator): %s' % criterion
                else:
                    criteria.append(tokens)

        if not err_msg and not criteria:
            err_msg = 'No criteria given.'

        if err_msg:
            self.write('2 %s' % err_msg)


        # Find all matching messages.
        # ===========================

        filters = []
        for header, op, sought in criteria:
            msg_ids = sets.Set()
            db_path = os.path.join(self.metadata_root, header.lower())
            if not os.path.isfile(db_path):
                continue
            db = anydbm.open(db_path)
            for msg_id, value in db.items():
                sought = repr(codecs.escape_encode(sought)[0])
                if op == '=':
                    op = '=='
                value = repr(codecs.escape_encode(value)[0])
                condition = ' '.join((value, op, sought))
                logger.debug('evaluating: %s' % condition)
                if eval(condition):
                    msg_ids.add(msg_id)
            filters.append(msg_ids)
            db.close()
        for filt in filters:
            msg_ids &= filt


        # Write their message IDs out to the wire.
        # ========================================

        self.write('1 Message IDs follow.')
        for msg_id in msg_ids:
            self.write(msg_id)
        self.write()


    def headers(self, msg_id):
        """Given a message ID, retrieve the message's headers.
        """
        path = os.path.join(self.data_root, msg_id)
        if os.path.isfile(path):
            msg = open(path, 'rb').read()
            msg = self.crypter.decrypt(msg)
            msg = self.padder.unpad(msg)
            headers = msg.split('\n\n', 1)[0]
            self.write('0 %s' % self.wrapper.wrap(headers))
        else:
            self.write('2 No such message.')


    def remove(self, msg_id):
        """Given a message ID, remove the message.
        """
        path = os.path.join(self.data_root, msg_id)
        if os.path.isfile(path):
            enc = open(path, 'rb').read()
            msg = self.crypter.decrypt(enc)
            msg = self.padder.unpad(msg)
            msg = message_from_string(msg)
            for header in sets.Set(msg.keys()):
                db_path = os.path.join(self.metadata_root, header.lower())
                db = anydbm.open(db_path, 'w')
                del db[msg_id]
                if len(db) > 0:
                    db.close()
                else:
                    db.close()
                    os.remove(db_path)
            os.remove(path)
            self.write('0 Message removed.')
        else:
            self.write('2 Message already removed.')


    def replace(self, msg_id, msg):
        """Replace one message with another.

        This does a store and a remove within one transaction, and is
        effectively an update operation. The wrinkle is that to us, the contents
        of the file determine its uniqueness, but any given application will
        undoubtedly impute identity to messages that according to our definition
        are not identical. Since any such imputation is application dependant,
        we don't support it beyond this convenience method.

        Note that this implementation is not actually transactional.

        """

        # Encrypt the message and generate a message ID.
        # ==============================================

        msg = self.wrapper.unwrap(msg)
        enc = self.padder.pad(msg)
        enc = self.crypter.encrypt(enc)
        msg_id = sha.new(enc).hexdigest()


        # Write the message to disk.
        # ==========================

        path = os.path.join(self.data_root, msg_id)

        if msg_id not in os.listdir(self.data_root):
            fp = file(path, 'w+b')
            fp.write(enc)
            fp.close()
        else:
            self.write('2 Already stored.')


        # Make sure we stored it successfully.
        # ====================================

        disk = open(path, 'rb').read()
        disk_id = sha.new(disk).hexdigest()
        if disk_id != msg_id:
            self.write('2 Message storage failed!')


        # Index the new message.
        # ======================

        for header, value in message_from_string(msg).items():
            db_path = os.path.join(self.metadata_root, header.lower())
            db = anydbm.open(db_path, 'c')
            db[msg_id] = value
            db.close()


        # Remove the old message.
        # =======================

        path = os.path.join(self.data_root, msg_id)
        if os.path.isfile(path):
            enc = open(path, 'rb').read()
            msg = self.crypter.decrypt(enc)
            msg = self.padder.unpad(msg)
            msg = message_from_string(msg)
            for header in sets.Set(msg.keys()):
                db_path = os.path.join(self.metadata_root, header.lower())
                db = anydbm.open(db_path, 'w')
                del db[msg_id]
                if len(db) > 0:
                    db.close()
                else:
                    db.close()
                    os.remove(db_path)
            os.remove(path)
        else:
            self.write('2 Already removed.')

        self.write('0 %s' % disk_id)


    def retrieve(self, msg_id):
        """Given a message ID, retrieve the message.
        """
        path = os.path.join(self.data_root, msg_id)
        if os.path.isfile(path):
            msg = open(path, 'rb').read()
            msg = self.crypter.decrypt(msg)
            msg = self.padder.unpad(msg)
            self.write('0 %s' % self.wrapper.wrap(msg))
        else:
            self.write('2 No such message.')


    def stop(self):
        """Stop the conversation.
        """
        self.write('0 Bye!')
        raise Done


    def store(self, msg):
        """Given a message, store it.
        """

        # Encrypt the message and generate a message ID.
        # ==============================================

        msg = self.wrapper.unwrap(msg)
        enc = self.padder.pad(msg)
        enc = self.crypter.encrypt(enc)
        msg_id = sha.new(enc).hexdigest()


        # Write the message to disk.
        # ==========================

        path = os.path.join(self.data_root, msg_id)

        if msg_id not in os.listdir(self.data_root):
            fp = file(path, 'w+b')
            fp.write(enc)
            fp.close()
        else:
            self.write('2 Already stored.')


        # Make sure we stored it successfully.
        # ====================================

        disk = open(path, 'rb').read()
        disk_id = sha.new(disk).hexdigest()
        if disk_id != msg_id:
            self.write('2 Message storage failed! (server)')


        # Index and return.
        # =================

        for header, value in message_from_string(msg).items():
            db_path = os.path.join(self.metadata_root, header.lower())
            db = anydbm.open(db_path, 'c')
            db[msg_id] = value
            db.close()

        self.write('0 %s' % disk_id)



class smapd(TCPServer537):
    """
    """

    def respond(self, incoming, outgoing):
        """
        """
        conversation = Conversation(incoming, outgoing)
        try:
            conversation.have()
        except Done:
            pass
        except:
            logger.error(traceback.format_exc())
            err_msg = '3 Internal server error.\n'
            logger.debug(err_msg)
            outgoing.write(err_msg)


if __name__ == '__main__':
    smapd().start()
