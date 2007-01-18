#!/usr/local/bin/python
"""For usage, see the sanity(1) manual page.

- It's a problem that DNS problems with domains not under my control can trigger
    an error (and SMS flood)

"""
import dbm
import httplib
import socket
import sys
import time
import traceback
import os
from ConfigParser import RawConfigParser, NoOptionError
from popen2 import Popen3
from urlparse import urlparse


class Sanity:

    def __init__(self):

        self.verbose = sys.argv[1:2] == ['-v']
        self.VERBOSE = sys.argv[1:2] == ['-V']
        if self.VERBOSE:
            self.verbose = True
        self.output = {}
        self.errors = []


        # Read in config info.
        # ====================

        CP = RawConfigParser()
        CP.read('/usr/local/etc/sanity.conf')
        self.badconfig = False
        keys = dict(CP.items('default')).keys()
        keys.sort()
        if keys <> [ 'email_addy'
                   , 'porter_path'
                   , 'redirects'
                   , 'server_ip'
                   , 'timeout'
                   ]:
            self.badconfig = True
            print "/usr/local/etc/sanity.conf is missing keys"
        else:
            self.porter_path = CP.get('default', 'porter_path')
            self.server_ip   = CP.get('default', 'server_ip')
            self.email_addy  = CP.get('default', 'email_addy')
            self.redirects   = int(CP.get('default', 'redirects'))
            self.timeout     = float(CP.get('default', 'timeout'))


            # Sync our porter data and read it in.
            # ====================================

            os.system('/usr/local/bin/svn cleanup %s' % self.porter_path)
            if self.verbose:
                sys.stdout.write('syncing dbm ...')
                os.system('/usr/local/bin/svn up %s' % self.porter_path)
                print ' done'
            else:
                os.system('/usr/local/bin/svn up --quiet %s' % self.porter_path)

            if self.verbose:
                sys.stdout.write('reading dbm ...')
            dbm_path = '%s/rewrite' % self.porter_path
            db = dbm.open(dbm_path, 'r')
            self.rawdata = dict(db)
            db.close()
            if self.verbose:
                print ' done'


    def __call__(self):
        """Assuming our config is readable, do our checks.
        """

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
                    s = (numerrors != 1) and 's' or ''
                    sub = "%s @ %s" % ( self.output['numerrors']
                                      , time.strftime( '%I:%M%p'
                                                     , time.localtime()
                                                      )
                                       )
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
        websites.sort(self.domain_cmp)
        websites = [w for w in websites if not w.startswith('www.')]

        self.output['numwebsites'] = len(websites)
        self.output['redirects'] = self.output['errors'] = self.output['warnings'] = self.output['clear'] = ''
        self.output['numredirects'] = self.output['numerrors'] = self.output['numwarnings'] = self.output['numclear'] = 0

        if self.verbose:
            sys.stdout.write('checking sites ')

        for website in websites:

            if self.VERBOSE:
                print >> sys.stderr, website
                sys.stderr.flush()
            elif self.verbose:
                sys.stdout.write('.')
                sys.stdout.flush()


            # Try to connect on port 80.
            # ==========================
            # If this fails, it means that all of zetaserver is down and it
            # should fail for all sites.
            #
            #   is this actually true? [cwlw; 2006-06-15]

            try:
                self.check_website(website, website, 0)
            except: # HTTP exception handling is lower down in hit_website
                traceback.print_exc()
                
        if self.verbose:
            print ' done'


    def check_website(self, current, original, i):
        """Recursive function to follow redirects.
        """
        status, line, location = self.hit_website(current, i)
        if status == 200:
            if i == 0:
                self.output['numclear'] += 1
                self.output['clear'] += line
            else:
                self.output['numredirects'] += 1
                self.output['redirects'] += line
        elif status in (301, 302):
            if (i == 0):
                self.output['numredirects'] += 1
            self.output['redirects'] += line
            assert location is not None, 'Location missing for %s' % current
            if i > self.redirects : # safety belt
                msg = "XXX  %s (more than %d redirects)\n" % ( original
                                                             , self.redirects
                                                              )
                self.output['errors'] += msg
                self.output['numerrors'] += 1
                self.errors.append(original)
            else:
                if location.startswith('/'): # just the path 
                                             # @@ bug here if the first redirect
                                             # is /foo and the second includes 
                                             # a host
                    location = 'http://%s%s' % (original, location)
                self.check_website(location, original, i+1)
        else:
            self.output['numerrors'] += 1
            self.output['errors'] += line
            self.errors.append(original)
                
            

    def hit_website(self, website, i):
        """Hit the website; return status, line, location (for redirects).
        """
        start = time.time()
        http = None
        try:
            try:

                # Parse the website string.
                # =========================
                # The ones coming from our database are the hostname only, 
                # but if we get a redirect it will be a full URL.
                
                host = website
                port = 80
                path = '/'
                
                if '://' in website:
                    scheme, netloc, path, params, query, frag = urlparse(website)
                    if ':' in  netloc:
                        assert netloc.count(':') == 1 # sanity check
                        host, port = netloc.split(':')
                        port = int(port)
                    else:
                        assert scheme in ('http', 'https')
                        host = netloc
                        if scheme == 'http':
                            port = 80
                        elif scheme == 'https':
                            port = 443
        
        
                # Make the connection, monitoring the getaddrinfo call.
                # =====================================================
                # I'm seeing this behavior: a domain with bad DNS takes
                # forever in the next call, but still returns 200
                # eventually. I can get the page with fetch, but Firefox
                # times out much earlier. We want to flag this condition.
        
                http = httplib.HTTPConnection(host, port)
                res = socket.getaddrinfo( http.host
                                        , http.port
                                        , socket.AF_INET
                                        , socket.SOCK_STREAM
                                        , socket.IPPROTO_TCP
                                         )[0]
                so_far = time.time() - start
                if so_far > self.timeout:
                    raise socket.error("getaddrinfo returned")
        
        
                # Proceed.
                # ========
        
                af, socktype, proto, canonname, sa = res
                http.sock = socket.socket(af, socktype, proto)
                http.sock.settimeout(self.timeout)
                http.sock.connect(sa)
        
                http.request('GET', path)
                response = http.getresponse()
                status = response.status
                line = '%s%s  %s' % (' '*i, status, website)
                if len(line) >= 79:
                    line = line[:76] + '...'
                line += '\n'
                location = response.getheader('Location', None)
                
                return status, line, location
                
            except socket.error, msg:
                end = time.time()
                msg = 'XXX  %s (%s after %d seconds)\n' % ( website
                                                          , msg
                                                          , (end-start)
                                                           )
                self.output['errors'] += msg
                self.output['numerrors'] += 1
                self.errors.append(website)
                raise

        finally:
            if http is not None:
                http.close()


    def domain_cmp(self, x, y):
        """[ripped from porter.py]

        Given two domain names, return -1, 0, or 1

        Domain names must be at least two places long, i.e, example.com, not com

        first sort on SLD (second level domain)
        then sort on TLD
        then sort on tertiary

        """
        # convert to lists, checking for bad data
        try:    d1 = x.split('.')
        except: raise PorterError, "unable to parse '%s' as a domain name" % x
        try:    d2 = y.split('.')
        except: raise PorterError, "unable to parse '%s' as a domain name" % y

        # more data checks
        if len(d1) < 2:
            raise PorterError, "'%s' doesn't look like a full domain name" % x
        if len(d2) < 2:
            raise PorterError, "'%s' doesn't look like a full domain name" % y

        # marshall into the order we want for sorting
        d1tertiary = d1[:-2]; d1tertiary.reverse()
        d2tertiary = d2[:-2]; d2tertiary.reverse()
        d1 = [d1[-2], d1[-1], d1tertiary]
        d2 = [d2[-2], d2[-1], d2tertiary]

        # do the comparison
        if d1 == d2: return 0
        if d1 < d2: return -1
        if d1 > d2: return 1


    body = """

THE SERVER IS %(server)s

========================================
    %(numwebsites)s WEBSITES
========================================

%(numerrors)s ERROR(S)
----------------------------------------
%(errors)s

%(numredirects)s REDIRECT(S)
----------------------------------------
%(redirects)s

%(numclear)s ALL CLEAR
----------------------------------------
%(clear)s
"""


if __name__ == '__main__':
    sanity = Sanity()
    sanity()
