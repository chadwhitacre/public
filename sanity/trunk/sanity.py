#!/usr/local/bin/python
"""see man 1 sanity"""

import dbm, httplib, sys, os
from popen2 import Popen3
from ConfigParser import RawConfigParser, NoOptionError
from SocketServer import socket # only using socket.error
from Porter.Porter import Porter # used for sorting domains; that should be a lib

class Sanity:

    def __init__(self):

        self.verbose = sys.argv[1:2] == ['-v']
        self.output = {}
        self.errors = []


        ##
        # read in config info
        ##
        CP = RawConfigParser()
        CP.read('/usr/local/etc/sanity.conf')
        self.badconfig = False
        keys = dict(CP.items('default')).keys()
        keys.sort()
        if keys <> [ 'email_addy'
                   , 'porter_path'
                   , 'server_ip'
                   ]:
            self.badconfig = True
            print "/usr/local/etc/sanity.conf is missing keys"
        else:
            self.porter_path = CP.get('default', 'porter_path')
            self.server_ip   = CP.get('default', 'server_ip')
            self.email_addy  = CP.get('default', 'email_addy')

            ##
            # sync our porter data and read it in
            ##
            os.system('/usr/local/bin/svn cleanup %s' % self.porter_path)
            if self.verbose:
                sys.stdout.write('syncing dbm ...')
                os.system('/usr/local/bin/svn up %s' % self.porter_path)
                if self.verbose: print ' done'
            else:
                os.system('/usr/local/bin/svn up --quiet %s' % self.porter_path)

            if self.verbose: sys.stdout.write('reading dbm ...')
            dbm_path = '%s/var/rewrite' % self.porter_path
            db = dbm.open(dbm_path, 'r')
            self.rawdata = dict(db)
            db.close()
            if self.verbose: print ' done'



    def __call__(self):
        """assuming our config is readable, do our checks"""

        if not self.badconfig:
            self.check_ping()
            self.check_http() # sets output values w/in

            if self.verbose or self.errors:

                print self.body % self.output
                # note: use a MAILTO environment variable in cron to send a full
                # report to a regular admin account

                if self.errors:
                    # but we explicitly notify our email address if we have
                    # errors
                    numerrors = len(self.errors); numtoshow = 5
                    if numerrors == 1: s = ''
                    else: s = 's'
                    sub = "%s site%s down" % ( self.output['numerrors'], s)
                    if numerrors > numtoshow:
                        more = ['+ %s more' % (numerrors-numtoshow,)]
                        self.errors = self.errors[:numtoshow] + more
                    msg = '; '.join(self.errors)
                    msg = '%s: %s' % (sub, msg)
                    os.system("""echo "%s" | mail -s '%s' %s""" % (msg, sub,
                                                           self.email_addy))


    def check_ping(self):
        """check our IP address for ping, set output accordingly"""
        ping = Popen3('/sbin/ping -c1 -t1 -q %s' % self.server_ip).wait()
        if ping == 0:
            self.output['server'] = 'UP'
        else:
            self.output['server'] = 'DOWN'


    def check_http(self):
        """check websites for HTTP 200, set output accordingly"""

        websites = self.rawdata.keys()
        websites.sort(Porter._domain_cmp)
        websites = [w for w in websites if not w.startswith('www.')]

        self.output['numwebsites'] = len(websites)
        self.output['errors'] = self.output['warnings'] = self.output['clear'] = ''
        self.output['numerrors'] = self.output['numwarnings'] = self.output['numclear'] = 0

        if self.verbose: sys.stdout.write('checking sites ')

        for website in websites:

            if self.verbose:
                sys.stdout.write('.'); sys.stdout.flush()

            # try to connect on port 80; if this fails, it means that all of
            # zetaserver is down and it should fail for all sites

            try:
                http = httplib.HTTPConnection(website,80)
                http.connect()
            except socket.error:
                self.output['errors'] += 'XXX  %s' % website
                continue

            # write output based on site status
            http.request('GET','/')
            status = http.getresponse().status
            line = '%s  %s\n' % (status, website)
            if status == 200:
                self.output['numclear'] += 1
                self.output['clear'] += line
            elif str(status)[0] == '3':
                self.output['numwarnings'] += 1
                self.output['warnings'] += line
            else:
                self.output['numerrors'] += 1
                self.output['errors'] += line
                self.errors.append(website)
            http.close()

        if self.verbose: print ' done'

    body = """

THE SERVER IS %(server)s

========================================
    %(numwebsites)s WEBSITES
========================================

%(numerrors)s ERROR(S)
----------------------------------------
%(errors)s

%(numwarnings)s WARNING(S)
----------------------------------------
%(warnings)s

%(numclear)s ALL CLEAR
----------------------------------------
%(clear)s
"""


if __name__ == '__main__':
    Sanity = Sanity()
    Sanity()