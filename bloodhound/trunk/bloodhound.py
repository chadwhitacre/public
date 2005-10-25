#!/usr/bin/env python
"""Bloodhound -- a metadata indexing daemon.
"""

import email
import os
import sets
import signal
import stat
import time
import traceback

from rdflib import Graph, Literal, Namespace, URIRef, BNode, RDF

from passwd import Passwd


NS_STAT = Namespace("http://localhost/stat#")
NS_STAT_KEYS = ( 'ST_MODE'
               , 'ST_INO'
               , 'ST_DEV'
               , 'ST_NLINK'
               , 'ST_UID'
               , 'ST_GID'
               , 'ST_SIZE'
               , 'ST_ATIME'
               , 'ST_MTIME'
               , 'ST_CTIME'
                )

NS_PASSWD = Namespace("http://localhost/passwd#")
NS_PASSWD_KEYS = ( 'name'
                 , 'password'
                 , 'uid'
                 , 'gid'
                 , 'class'
                 , 'change'
                 , 'expire'
                 , 'gecos'
                 , 'home_dir'
                 , 'shell'
                  )

NS_MIME = Namespace("http://localhost/mime#")

NS_USERS = Namespace("http://localhost/users#")
NS_FILES = Namespace("http://localhost/files#")


def signum2name(signum):
    signame = '<unknown>'
    for name, num in signal.__dict__.items():
        if num == signum:
            signame = name
            break
    return signame



class Bloodhound:

    def __init__(self, dataroot='/var/db/data', metaroot='/var/db/meta'):
        """
        """

        if not os.path.isdir(dataroot):
            raise SystemExit('Data root does not exist')
        if not os.path.isdir(metaroot):
            raise SystemExit('Metadata root does not exist')

        self.passwd = Passwd('/etc/master.passwd')

        self.dataroot = dataroot
        self.db = Graph('Sleepycat')
        self.db.open(metaroot)
        self.db.bind('files',   unicode(NS_FILES.abstract()),   True)
        self.db.bind('mime',    unicode(NS_MIME.abstract()),    True)
        self.db.bind('passwd',  unicode(NS_PASSWD.abstract()),  True)
        self.db.bind('stat',    unicode(NS_STAT.abstract()),    True)
        self.db.bind('users',   unicode(NS_USERS.abstract()),   True)

        self.known_files = {}
        self.known_users = ()

        signal.signal(signal.SIGTERM, self.calloff)
        signal.signal(signal.SIGINT, self.calloff)
        signal.signal(signal.SIGUSR1, self.dump)
        signal.signal(signal.SIGUSR2, self.sniff_safely)

        file('/var/run/bloodhound.pid', 'w').write(str(os.getpid()))


    # Top-level callables; startup and signal handling.
    # =================================================

    def sic(self):
        """Proactively sniff.
        """
        while 1:
            self.sniff_safely()
            time.sleep(1)


    def ready(self):
        """Wait for SIGUSR2.
        """
        while 1:
            time.sleep(0.5)


    def calloff(self, num, frame):
        """Hook to properly shutdown database on exit.
        """
        print "\nreceived %s, shutting down" % signum2name(num)
        self.db.close()
        os.remove('/var/run/bloodhound.pid')
        raise SystemExit


    def dump(self, num, frame):
        """For debugging; handler for SIGUSR1.
        """
        try:
            print "Contents of metadata database"
            print "="*79
            print self.db.serialize(format='pretty-xml')
        except:
            print traceback.format_exc()


    # Worker bee.
    # ===========

    def sniff_safely(self, num=None, frame=None):
        """Look for changes to users, groups, and files under our watch.
        """
        if num is not None:
            print "caught %s, sniffing" % signum2name(num)
        try:
            self.sniff()
        except StandardError:
            print traceback.format_exc()
        if num is not None:
            print "done sniffing"


    def sniff(self):
        """Look for changes to users, groups, and files under our watch.
        """

        # Users
        # =====

        # added/modified
        if self.passwd.synced < os.stat('/etc/master.passwd')[stat.ST_MTIME]:
            self.passwd.load()
            known_users = []
            for rec in self.passwd.values():
                uri = NS_USERS[rec.name]
                if rec.uid == 0:                    # don't index root
                    continue
                elif rec.password == '*':           # don't index non-logins
                    continue
                elif rec.shell == '/sbin/nologin':  # don't index non-logins
                    continue
                else:
                    self.db_index_user(uri, rec)
                    known_users.append(uri)
            self.known_users = tuple(known_users)

        # removed
        removed = self.db_known(NS_USERS).difference(self.known_users)
        if removed:
            for uri in removed:
                self.db_prune(uri)


        # Files
        # =====
        # We weigh both content and fs metadata changes equally.

        # added/modified
        known_uris = []
        for filename in os.listdir(self.dataroot):

            uri = NS_FILES[filename]
            known_uris.append(uri)
            stats = os.stat(os.path.join(self.dataroot, filename))
            mtime = stats[stat.ST_MTIME]
            ctime = stats[stat.ST_CTIME]

            new_file = uri not in self.known_files
            times = self.known_files.get(uri, (0,0))
            modified = (mtime > times[0]) or (ctime > times[1])
            if new_file or modified:
                self.db_index_file(uri, stats)
                self.known_files[uri] = (mtime, ctime)

        # removed
        removed = self.db_known(NS_FILES).difference(known_uris)
        if removed:
            for uri in removed:
                self.db_prune(uri)



    # db access.
    # ==========

    def db_index_user(self, uri, rec):
        """Index a user, return its URI.
        """
        #print "indexing user %s [passwd]" % rec.name
        s = uri
        for key in NS_PASSWD_KEYS:
            p = NS_PASSWD[key]
            o = Literal(rec[key])
            #print '  ', (s,p,o)
            self.db.add((s,p,o))
        print "indexed %s" % uri


    def db_index_file(self, uri, stats):
        """Index an file, return its URI.
        """
        filename = uri.rsplit('#', 1)[1]
        s = uri

        #print "indexing file %s [stat]" % filename
        for key in NS_STAT_KEYS:
            p = NS_STAT[key]
            o = Literal(stats[getattr(stat, key)])
            #print '  ', (s,p,o)
            self.db.add((s,p,o))

        #print "indexing file %s [MIME]" % filename
        filepath = os.path.join(self.dataroot, filename)
        msg = email.message_from_file(open(filepath))
        for key, val in msg.items():
            p = NS_MIME[key]
            o = Literal(val)
            #print '  ', (s,p,o)
            self.db.add((s,p,o))

        print "indexed %s" % uri


    def db_known(self, namespace):
        """Return a Set of the subjects that we know about within a Namespace.
        """
        known = sets.Set()
        #print unicode(namespace.abstract())
        for s,p,o in self.db.triples((None,None,None)):
            #print unicode(s)
            if unicode(s).startswith(unicode(namespace.abstract())):
                #print "BLAM!!!!!!!!!!!!!!!!!!"
                known.add(s)
        return known


    def db_prune(self, dead_uri):
        """Prune references to a removed resource.
        """
        # subjects
        for s,p,o in tuple(self.db.triples((dead_uri, None, None))):
            self.db.remove((s,p,o))
        # predicates
        for s,p,o in tuple(self.db.triples((None, None, dead_uri))):
            self.db.remove((s,p,o))
        print "pruned %s" % str(dead_uri)



if __name__ == '__main__':
    bloodhound = Bloodhound()
    bloodhound.sniff()
    bloodhound.ready()