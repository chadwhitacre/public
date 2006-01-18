#!/usr/bin/env python
"""mimefsd -- a MIME filesystem XMLRPC server.
"""

__version__ = (0, 4)
__author__ = 'Chad Whitacre <chad@zetaweb.com>'

import codecs
import logging
import os
import sets
import sha
import signal
import subprocess
import sys
import time
from StringIO import StringIO
from email import message_from_string
from email.Generator import Generator
from email.Message import Message

import psycopg
from httpy.Config import ConfigError
from httpy.Config import Config
from httpy.Server import Server
from httpy.Server import RestartingServer
from httpy.apps.XMLRPC import XMLRPCApp


format = "%(name)-16s %(levelname)-8s %(message)s"
logging.basicConfig( level=logging.DEBUG
                   , format=format
                    )
logger = logging.getLogger('mimefsd')


# TODO: add check for ownership and permissions
KEY = open('/etc/mimefs.key').read()


# Monkey-patch Task since we don't have anything on the filesystem.
# =================================================================

from httpy.Task import Task
def _validate(self):
    pass
Task.validate = _validate


# Define our Application class.
# =============================

OPERATORS = ('>', '>=', '=', '!=', '<=', '<', 'startswith', 'endswith')

class mimefsdError(StandardError):
    """
    """

class Application(XMLRPCApp):

    uri_root = '/' # To play nice with httpy until it is more library-friendly.


    # Fundaments
    # ==========

    def echo(self, foo=''):
        return foo

    def _connect(self):
        """Given a database name, return a database connection.
        """
        return psycopg.connect('dbname=mimefs_0')

    def _verify_key(self, key):
        """Given the master key, verify that it is correct.
        """
        if key != KEY:
            raise mimefsdError("Bad key: '%s'" % key)

    def _verify_vid(self, vid):
        """Given a vid, verify that it exists.
        """
        conn = self._connect()
        curs = conn.cursor()

        SQL = "SELECT vid FROM volume WHERE vid=%s;"
        curs.execute(SQL, (vid,))
        if curs.rowcount == 0:
            raise mimefsdError("Bad vid: '%s'" % vid)
        elif curs.rowcount == 1:
            return None
        else:
            raise mimefsdError("Wacky rowcount: %s" % curs.rowcount)

    def _uuid(self):
        """Return a universally unique identifier, version 4 (RFC 4122).

        Currently we depend on uuid(1) in the OS; should change to uuidgen?

        """
        proc = subprocess.Popen(('uuid','-v4'), stdout=subprocess.PIPE)
        return proc.stdout.read().strip('\n')


    # Volumes
    # =======

    def list(self, key):
        """Return a list of all vids.
        """
        self._verify_key(key)
        conn = self._connect()
        curs = conn.cursor()

        SQL = "SELECT vid FROM volume;"
        curs.execute(SQL)
        vids = [row[0] for row in curs.fetchall()]

        conn.commit()
        conn.close()
        return vids


    def newvol(self, key):
        """Given the master key, return the vid of a new volume.
        """
        self._verify_key(key)
        conn = self._connect()
        curs = conn.cursor()

        vid = self._uuid()
        SQL = "INSERT INTO volume (vid) VALUES (%s);"
        curs.execute(SQL, (vid,))

        conn.commit()
        conn.close()
        return vid


    def rmvol(self, key, vid):
        """Takes the master key and a vid.

        The tables are wired such that when a volume is removed, all messages
        in that volume are automatically removed, and their metadata is
        unindexed.

        """
        self._verify_key(key)
        conn = self._connect()
        curs = conn.cursor()

        SQL = "DELETE FROM volume WHERE vid=%s;"
        curs.execute(SQL, (vid,))

        conn.commit()
        conn.close()



    # Message location and removal.
    # =============================
    # The following all operate on a single volume.

    def exists(self, mid):
        """Given a mid, return True or False.
        """
        conn = self._connect()
        curs = conn.cursor()

        SQL = "SELECT mid FROM message WHERE mid=%s;"
        curs.execute(SQL, (mid,))
        if curs.rowcount == 0:
            val = False
        elif curs.rowcount == 1:
            val = True
        else:
            raise mimefsdError("Wacky rowcount: %s" % curs.rowcount)

        conn.commit()
        conn.close()
        return val


    def list(self, vid, WHERE='', LIMIT='ALL', OFFSET=0):
        """Given optional constraints, return mids.

        This is brute force unoptimized. You have been warned. :^)

        One idea for optimization is to require certain metadata, such as
        Content-Type and Modification-Time. Think of the most common listing
        cases. Another idea is to push the filtering logic down into a
        PostgreSQL procedure. The more radical idea is to actually create
        columns for metadata and use native SQL joins, etc. rather than
        reimplementing all of this set malarky at a higher level.

        """
        conn = self._connect()
        curs = conn.cursor()


        # Parse and validate constraints.
        # ===============================

        criteria = []
        for criterion in WHERE.splitlines():
            tokens = criterion.split(None, 2)
            if len(tokens) != 3:
                mimefsdError( "Bad criterion (too few tokens): " +
                              "'%s'" % criterion
                             )
            else:
                tokens[1] = tokens[1].lower()
                if tokens[1] not in OPERATORS:
                    mimefsdError( "Bad criterion (bad operator): " +
                                  "'%s'" % criterion
                                 )
                else:
                    criteria.append(tokens)
        if (LIMIT != 'ALL') and not isinstance(LIMIT, int):
            raise mimefsdError("Bad limit: '%s'" % LIMIT)
        if OFFSET and not isinstance(OFFSET, int):
            raise mimefsdError("Bad offset: '%s'" % OFFSET)


        # Find all matching messages.
        # ===========================

        if not criteria:

            SQL = "SELECT mid FROM message ORDER BY mid;"
            curs.execute(SQL)
            mids = [row[0] for row in curs.fetchall()]

        else:

            filters = []

            for name, op, sought in criteria:
                mids = sets.Set()

                # Massage our input.
                # ==================

                name = name.lower() # case-insensitive
                if op == '=':
                    op = '=='
                if len(op) > 2: # startswith, endswith
                    condition_tmpl = '%(body)s.%(op)s(%(sought)s)'
                else:
                    condition_tmpl = '%(body)s%(op)s%(sought)s'
                sought = repr(codecs.escape_encode(sought)[0])


                # Get candidate fields.
                # =====================

                SQL = """\
                    SELECT f.mid, f.body
                      FROM field f
                      JOIN message m
                        ON f.mid = m.mid
                     WHERE m.vid = %s
                       AND f.name = %s;
                     """
                curs.execute(SQL, (vid, name))


                # Loop through and find matches.
                # ==============================

                for mid, body in curs.fetchall():
                    vals = {}
                    vals['sought'] = sought
                    vals['op'] = op
                    vals['body'] = repr(codecs.escape_encode(body)[0])
                    condition = condition_tmpl % vals
                    logger.debug('evaluating: %s' % condition)
                    if eval(condition):
                        mids.add(mid)

                filters.append(mids)

            for filt in filters:
                mids &= filt
            mids = tuple(mids)


        # Slice, dice, and return.
        # ========================

        if LIMIT == 'ALL':
            LIMIT = len(mids)
        mids = mids[OFFSET:OFFSET+LIMIT]
        conn.commit()
        conn.close()
        return mids


    def open(self, vid, headers='', create=True, exclusive=True,
             truncate=False):
        """Given a vid, and an optional header block and flags, return a mid.

        In mimefs, a set of headers is parallel to a path on traditional
        filesystems: it identifies a particular point in the datastore. On that
        parallel, this call behaves as follows based on the number of messages
        matched by the given headers:

            0 messages matched
                If create is True, we create a new message with the given
                headers and return its mid. Otherwise we raise an error.

            1 message matched
                We return the mid of the message. If truncate is True, the
                message body is truncated to zero length. If both exclusive and
                create are True we raise an error.

            >1 messages matched
                We raise an error.


        mimefs does not implement caching, linking, locking or protection.

        """
        conn = self._connect()
        curs = conn.cursor()


        # Validate vid.
        # =============

        if vid:
            SQL = "SELECT vid FROM volume WHERE vid=%s;"
            curs.execute(SQL, (vid,))

            if curs.rowcount == 0:
                raise mimefsError("Bad vid: '%s'" % vid)
            elif curs.rowcount == 1:
                pass
            else:
                raise mimefsdError("Wacky rowcount: '%s'" % curs.rowcount)


        # Branch based on matched messages.
        # =================================

        mids = self.list(vid, headers, LIMIT=2)
        matches = len(mids)

        if matches == 0:
            if create:
                mid = self._uuid()
                SQL = "INSERT INTO message (vid, mid) VALUES (%s, %s)"
                curs.execute(SQL, (vid, mid, headers))

            else:
                raise mimefsdError("Message does not exist.")

        elif matches == 1:
            if create and exclusive:
                raise mimefsdError("Message already exists.")
            if truncate:
                mid = mids[0]
                self.write(vid, mid, '')

        elif matches == 2:
            raise mimefsdError("More than one message.")

        else:
            raise mimefsdError("Total botch.")


        conn.commit()
        conn.close()
        return mid


    def remove(self, vid, mid):
        """Given a mid, remove a message, returning None.

        The metadata unindexing is handled by a constraint in the table
        definition.

        """
        conn = self._connect()
        conn.close()

        SQL = "DELETE FROM message WHERE mid=%s;"
        curs.execute(SQL, (mid,))

        conn.commit()
        conn.close()
        return None



    # Message access and storage.
    # ===========================
    # The following all operate on a single message.

    def read(self, vid, mid, headers_only=False):
        """Given a vid and a mid, return the message as a string.

        If headers_only is True, only the message's header block is returned.

        The mid is globally unique, but as a precaution we also use the vid.

        """
        conn = self._connect()
        curs = conn.cursor()


        # Get data.
        # =========

        what = 'headers, body'
        if headers_only:
            what = 'headers'
        SQL = "SELECT %s FROM message WHERE vid=%%s AND mid=%%s;" % what
        curs.execute(SQL, (vid, mid))


        # Validate.
        # =========

        if curs.rowcount == -1:
            raise mimefsdError("Error running query.")
        if curs.rowcount == 0:
            raise mimefsdError("No message found.")
        elif curs.rowcount > 1:
            raise mimefsdError( "mid matched %s " % str(curs.rowcount) +
                                "messages; probable data corruption!"
                               )

        # Return.
        # =======

        if headers_only:
            message = curs.fetchone()[0]
        else:
            message = '\r\n\r\n'.join(curs.fetchone()[0])
        conn.commit()
        conn.close()
        return message


    def write(self, vid, mid, msg, headers_only=False):
        """Given a mid and a MIME message, store and index.

        If headers_only is False, then a msg without two line breaks is
        interpreted as a body part, which is stored without changing the index.

        If headers_only is True, then a msg without two line breaks is
        interpreted as a header block, and any body part in msg is optional and
        will be ignored.

        """
        self._verify_vid(vid)
        conn = self._connect()
        curs = conn.cursor()


        # Break msg into headers and body.
        # ================================
        # Convert all newlines to \r\n per RFC 822/2045, and make sure a
        # body-less or header-less message has two line breaks. Then split it.

        msg = '\r\n'.join(msg.splitlines())
        if '\r\n\r\n' not in msg:
            if flags[W_HDONLY]:
                msg += '\r\n\r\n'
            else:
                msg = '\r\n\r\n' + msg
        headers, body = msg.split('\r\n\r\n', 1)


        # Determine the mid.
        # ==================
        # If given a valid mid, unindex it.

        if not mid:
            mid = self._uuid()
        else:
            SQL = "SELECT mid FROM message WHERE mid=%s;"
            curs.execute(SQL, (mid,))
            if curs.rowcount == 1:
                SQL = "DELETE FROM field WHERE mid=%s;"
                curs.execute(SQL, (mid,))
            else:
                raise mimefsdError("Bad mid: '%s'" % mid)


        # Now store and index the message.
        # ================================

        if headers_only:
            # Note that we don't want to overwrite any existing body.
            SQL = ( "INSERT INTO message (vid, mid, headers) " +
                    "VALUES (%s, %s, %s);"
                   )
            curs.execute(SQL, (vid, mid, headers))
        else:
            SQL = ( "INSERT INTO message (vid, mid, headers, body) " +
                    "VALUES (%s, %s, %s, %s);"
                   )
            curs.execute(SQL, (vid, mid, headers, body))

        for name, body in message_from_string(headers).items():
            name = name.lower() # case insensitive
            SQL = "INSERT INTO field (mid, name, body) VALUES (%s, %s, %s);"
            curs.execute(SQL, (mid, name, body))


        # Wrap up and return.
        # ===================

        conn.commit()
        conn.close()
        return mid



# Define a callable to start the server.
# ======================================

def main(argv=None):

    # Read in configuration options.
    # ==============================
    # We override the default port number

    Config.address = ('', 5370)

    if argv is None:
        argv = sys.argv[1:]
    try:
        config = Config(argv)
    except ConfigError, err:
        print >> sys.stderr, err.msg
        print >> sys.stderr, "`man 1 mimed' for usage."
        return 2


    # Instantiate and start a server.
    # ===============================

    plain_jane = (  (os.environ['HTTPY_MODE'] == 'deployment')
                 or (sys.platform == 'win32')
                 or ('HTTPY_PLAIN_JANE' in os.environ)
                   )
    ServerClass = plain_jane and Server or RestartingServer
    server = ServerClass(config)
    server.apps = [Application()]
    server.start()


if __name__ == "__main__":
    sys.exit(main())
