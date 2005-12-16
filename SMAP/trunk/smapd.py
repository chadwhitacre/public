#!/usr/bin/env python

import anydbm
import base64
import bz2
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
ALLOWED = ( 'FIND'
          , 'HDRS'
          , 'RMV'
          , 'RTRV'
          , 'STOP'
          , 'STOR'
           )


class Done(StandardError):
    """Signal for the end of a conversation
    """


class Conversation:
    """Represents a persistent connection.
    """

    client_id = None
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

    def write(self, msg):
        if not msg.endswith('\n'):
            msg += '\n'
        logger.debug("SEND: %s" % msg.rstrip('\n'))
        self.out.write(msg)
        self.out.flush()



    # Main Loop
    # =========

    def have(self):
        """Have a conversation. Get it? Get it?
        """

        # First get the client ID
        # =======================

        self.write('1 SMAP/0.1 Welcome! Your client ID?')
        while not self.client_id:
            client_id = self.readline().rstrip('\n')
            if client_id in CLIENT_IDS:
                self.client_id = client_id
                self.data_root = os.path.join(ROOT, client_id, 'data')
                self.metadata_root = os.path.join(ROOT, client_id, 'metadata')
                self.write('1 Thanks! Your crypt key? (optional)')
            else:
                self.write('2 Bad client ID; try again.')


        # Second, get the optional encryption key
        # =======================================

        while not self.crypter:

            crypt_key = self.readline().rstrip('\n')

            if not crypt_key:
                self.crypter = smaplib.DummyCrypter()
                self.padder = smaplib.DummyPadder()
                self.write('0 Ok, your data will be stored unencrypted.')
            elif crypt_key.replace('-', '') == client_id:
                self.write("2 Crypt key can't match client ID.")
            elif len(crypt_key) != 32:
                self.write("2 Crypt key must be 32 bytes long.")
            else:
                self.crypter = AES.new(crypt_key)
                self.padder = smaplib.Padder()
                self.write('0 You have chosen ... wisely!')



        # Then they can do anything they want.
        # ====================================

        while 1:
            request = self.readline()
            if request == 'STOP\n':
                self.write('0 Bye!')
                raise Done
            else:
                tokens = request.split(None)
                try:
                    if len(tokens) != 2:
                        raise Done
                    command, argument = tokens
                    if command not in ALLOWED:
                        raise Done
                except Done:
                    self.write('2 Bad request.')
                else:
                    method = getattr(self, command)
                    method(argument)


    # Actual API
    # ==========

    def FIND(self, arg):
        """
        """
        self.write('3 Not implemented.')


    def HDRS(self, msg_id):
        """Given a message ID, retrieve the message's HeaDeRS.
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


    def RMV(self, msg_id):
        """Given a message ID, ReMoVe the message.
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
            self.write('1 Message already removed.')


    def RTRV(self, msg_id):
        """Given a message ID, ReTRieVe the message.
        """
        path = os.path.join(self.data_root, msg_id)
        if os.path.isfile(path):
            msg = open(path, 'rb').read()
            msg = self.crypter.decrypt(msg)
            msg = self.padder.unpad(msg)
            self.write('0 %s' % self.wrapper.wrap(msg))
        else:
            self.write('2 No such message.')


    def STOR(self, msg):
        """Given a message, STORe it.
        """

        # Encrypt the message and generate a message ID.
        # ==============================================

        msg = self.wrapper.unwrap(msg)
        enc = self.padder.pad(msg)
        enc = self.crypter.encrypt(enc)
        msg_id = sha.new(enc).hexdigest()


        # Write the message to disk.
        # ==========================

        already_stored = False
        path = os.path.join(self.data_root, msg_id)

        if msg_id not in os.listdir(self.data_root):
            fp = file(path, 'w+b')
            fp.write(enc)
            fp.close()
        else:
            already_stored = True


        # Make sure we stored it successfully.
        # ====================================

        disk = open(path, 'rb').read()
        disk_id = sha.new(disk).hexdigest()
        if disk_id != msg_id:
            self.write('2 Message storage failed! (server)')
            return


        # Index and return.
        # =================

        if not already_stored:
            for header, value in message_from_string(msg).items():
                db_path = os.path.join(self.metadata_root, header.lower())
                db = anydbm.open(db_path, 'c')
                db[msg_id] = value
                db.close()
        self.write('%s %s\n' % (int(already_stored), disk_id))



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
