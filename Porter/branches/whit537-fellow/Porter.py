"""

Porter is our Cmd app that manages rewrite.db. On program initialization, we
read data in from rewrite.db into an internal data structure, and we generate an
index that we use to present aliases for convenience. Then whenever we do one of
[mk, rm] we want to save our changes to the db.

"""

import cmd, datetime, dbm, os, shutil, sys, httplib
from SocketServer import socket # only using socket.error
from popen2 import Popen3
from base64 import b64decode
from cPickle import loads
from os.path import join

__version__ = 0.3

class PorterError(RuntimeError):
    """ error class for porter """
    pass

class Porter(cmd.Cmd):

    def __init__(self, *args, **kw):

        # set our data paths
        PKG_HOME = os.environ.get('PKG_HOME', sys.path[0])
        INSTANCE_HOME = os.environ.get('INSTANCE_HOME', PKG_HOME)
        self.var = join(INSTANCE_HOME, 'var')
        self.db_path = join(self.var, "rewrite")

        # we maintain five indices that are initialized on startup:
        #  self.aliases   - one-to-many mapping of server:port to domains
        #  self.domains   - one-to-many mapping of domains to server:port
        # the following three are not changed by porter (they are read-only)
        #  self.codenames - one-to-many mapping of server:ports to codenames
        #  self.servers   - mapping of hostnames to (status, numsites) tuples
        #  self.websites  - mapping of website ids to port numbers
        self._initialize_data()

        # let our superclass have its way too
        cmd.Cmd.__init__(self, *args, **kw)

        # ui settings
        year = datetime.date.today().year
        num = len(self.domains)
        if num == 1: word = 'domain'
        if num <> 1: word = 'domains'

        self.intro = """
#------------------------------------------------------------------------#
#  Porter v%s (c)2004-%s Zeta Design & Development <www.zetaweb.com>  #
#------------------------------------------------------------------------#

You are currently managing %s %s. Type ? for help.
        """ % (__version__, year, num, word)
        self.prompt = 'porter> '

    ##
    # Help
    ##

    def do_help(self, bar=""):

        if bar:
            cmd.Cmd.do_help(self, bar)

        else:
            print >> self.stdout, """\

Porter is a piece of software for managing the interface between the public
Internet and a server cluster set up according to the Cambridge distributed
http server architecture. For more on Cambridge ... um, talk to Chad. ;^)

Commands available:

    ls -- list available domains
          OPTIONS: -i/--info, -l/--long, -r/--raw, -s/-servers -w/--websites
          ARGS: With no options or with the -l option, ls takes an optional
                argument. If you pass in this argument, Porter only lists
                domains that begin with that value. So for example, 'ls zeta'
                would list zetaweb.com and zetaserver.com, but not
                sub1.zetaweb.com nor zogurt.org.
          Domains can be tab-completed.

    mk -- register a domain with Porter
          ARGS: domain server port, e.g.: example.com srvrname 8080
          ALIASES: add, mv
          Domains can be tab-completed with mv.

    rm -- unregister a domain
          ARGS: one or more space-separated domain names, e.g.: foo.example.net
          Domains can be tab-completed.
            """

    ##
    # Completes
    ##

    def _complete_domains(self, text, line, begidx, endidx):
        return [d for d in self.domains.keys() if d.startswith(text)]

    def _complete_websites(self, text, line, begidx, endidx):
        return [s for s in self.websites.keys() if s.startswith(text)]

    # this is the one that actually gets called
    def complete_smart(self, text, line, begidx, endidx):
        # determine position of argument, and return appropriate completion
        return self._complete_domains(text, line, begidx, endidx)


    ##
    # Create/Update
    ##

    complete_mv = complete_smart

    def do_mv(self, inStr=''):
        """ alias for mk, but with tab-completion """
        self.do_mk(inStr)

    def do_add(self, inStr=''):
        """ pure alias for mk """
        self.do_mk(inStr)

    def do_mk(self, inStr=''):
        """ given a domain name and a website, map them """

        # get our arguments and validate them
        opts, args = self._parse_inStr(inStr)
        if len(args) < 3:
            print >> self.stdout, "We need a domain name, a server name, " +\
                                  "and a port number."
            return
        domain, server, port = args[:3]
        if domain.startswith('www.'):
            print >> self.stdout, "Please do not include 'www' on domains."
            return
        # not worth validating port number since it will come from "dropdown" anyway
        # not worth validating server since it will come from "dropdown" anyway

        old_website = self.domains.get(domain)
        new_website = ':'.join((server,port))

        # update our data
        self.domains[domain] = new_website
        self._write_to_disk()

        # and update our index of aliases
        if old_website is not None:
            self.aliases[old_website].remove(domain)
        if new_website in self.aliases:
            if domain not in self.aliases[new_website]:
                self.aliases[new_website].append(domain)
        else:
            self.aliases[new_website] = [domain]
        self.aliases[new_website].sort(self._domain_cmp)


    ##
    # Read
    ##

    complete_ls = _complete_domains

    def do_ls(self, inStr=''):
        """ list various things we are managing """

        ##
        # first define our various listing methods
        ##

        def _list_domains(args):
            """ marshall and return domains list """
            domains = self.domains.keys()
            domains.sort(self._domain_cmp)
            if args:
                domains = [d for d in domains if d.startswith(args[0])]
            return domains

        def list_domains_short(args):
            """ format and output a basic domains listing """
            # columnize is an undocumented method in cmd.py
            domains = _list_domains(args)
            if domains: # otherwise columnize gives us '<empty>'
                self.columnize(domains, displaywidth=79)

        def list_domains_long(args):
            """ format and output an extended domains listing """
            domains = _list_domains(args)
            if domains:
                header = """
DOMAIN NAME               WEBSITE                   ALIASES
%s""" % (self.ruler*79,)
                print >> self.stdout, header
                for domain in domains:
                    server_port = self.domains[domain]
                    aliases = self.aliases[self.domains[domain]][:]
                    aliases.remove(domain) # don't list ourselves in
                                           # aliases

                    # format our fields
                    domain  = domain.ljust(24)[:24]
                    website = self.codenames.get(server_port)
                    if website is None:
                        website = 'MISSING@' + server_port
                    website = website.ljust(24)[:24]
                    if aliases: alias = aliases.pop(0)[:24]
                    else:       alias = ''

                    # build and output our record
                    record = "%s  %s  %s" % (domain, website, alias)
                    print >> self.stdout, record
                    for alias in aliases:
                        print >> self.stdout, ' '*50 + alias
                print >> self.stdout # newline

        def list_info(ignored):
            """ give some basic stats """
            num = len(self.domains)
            if num == 1: word = 'domain'
            if num <> 1: word = 'domains'
            print >> self.stdout, "You are currently managing " +\
                                  "%s %s." % (num, word)

        def list_raw(ignored):
            """ show exactly what is in our dbm """
            print >> self.stdout, """
KEY                           VALUE\n%s""" % (self.ruler*60,)
            raw = dbm.open(self.db_path,'r')
            for key in dict(raw):
                print >> self.stdout, "%s  %s" % (key.ljust(28),
                                                  raw[key].ljust(28))
            print >> self.stdout # newline
            raw.close()

        def list_servers(ignored):
            """ show what servers we know about """
            header = """
SERVER                          # WEBSITES      STATUS
%s""" % (self.ruler*79,)
            print >> self.stdout, header
            servers = self.servers.keys()
            if servers:
                servers.sort()
                for server in servers:

                    numsites, status = self.servers[server]

                    # format our fields
                    server   = server.ljust(30)[:30]
                    numsites = str(numsites).rjust(12)[:12]
                    status   = status.ljust(15)[:15]

                    # build and output our record
                    record = "%s  %s  %s" % (server, numsites, status)
                    print >> self.stdout, record
                print >> self.stdout # newline

        def list_websites(ignored):
            """ show what websites we know about """
            websites = self.websites.keys()
            if websites:
                websites.sort()
                self.columnize(websites, displaywidth=79)

        ##
        # and then pick one
        ##

        opts, args = self._parse_inStr(inStr)

        default = list_domains_short

        options = { 'd'         : list_domains_short
                  , 'domains'   : list_domains_short
                  , 'i'         : list_info
                  , 'info'      : list_info
                  , 'l'         : list_domains_long
                  , 'long'      : list_domains_long
                  , 'r'         : list_raw
                  , 'raw'       : list_raw
                  , 's'         : list_servers
                  , 'servers'   : list_servers
                  , 'w'         : list_websites
                  , 'websites'  : list_websites
                   }

        if opts:
            list_func = options.get(opts[0], default)
        else:
            list_func = default
        list_func(args)



    ##
    # Delete
    ##

    complete_rm = complete_ls

    def do_rm(self, inStr=''):
        """ given one or more domain names, remove it/them from our storage """
        opts, args = self._parse_inStr(inStr)
        for domain in args:

            if domain in self.domains:
                del self.domains[domain]
            else:
                print >> self.stdout, "%s is not in our database" % domain

            for website in self.aliases:
                if domain in self.aliases[website]:
                    self.aliases[website].remove(domain)

        self._write_to_disk()


    ##
    # Store
    ##

    def _initialize_data(self):
        """ populate our index attrs """

        # read in data from our db, which is a one-to-one mapping of domains
        #  to websites (website == server:port)
        db = dbm.open(self.db_path, 'c') # 'c' means create it if not there
        rawdata = dict(db)
        db.close()

        # should we do some integrity checking here? i.e., make sure that all
        # domains have a www counterpart? check for dupes?

        ##
        # self.domains
        ##
        # filter out www's for our users, we will add them back in when we
        #  write to disk
        domains = {}
        for domain in rawdata:
            if not domain.startswith('www.'):
                domains[domain] = rawdata[domain]

        ##
        # self.aliases
        ##
        aliases = {}
        for domain in domains:
            website = domains[domain]
            if website in aliases:
                aliases[website].append(domain)
            else:
                aliases[website] = [domain]

        ##
        # self.servers and self.websites
        ##
        servers, websites = self._available_websites()


        ##
        # self.codenames
        ##
        codenames = {}
        for website in websites:
            server_port = website.split('@')[1]
            codenames[server_port] = website

        self.aliases   = aliases.copy()
        self.codenames = codenames.copy()
        self.domains   = domains.copy()
        self.servers   = servers.copy()
        self.websites  = websites.copy()


    def _write_to_disk(self):
        """ given that our data is clean, store it to disk """

        # create a local copy of self.domains, adding www's back in
        db_records = {}
        for domain in self.domains:
            website = self.domains[domain]
            db_records[domain] = website
            db_records['www.' + domain] = website

        # back up the current file
        shutil.copyfile(self.db_path + '.db', self.db_path + '.db.old')

        # now write the new one
        db = dbm.open(self.db_path, 'n')
        for domain in db_records:
            db[domain] = db_records[domain]
        db.close()


    ##
    # Helpers
    ##

    def _parse_inStr(inStr):
        """ given a Cmd inStr string, return a tuple containing a list of
        options and a list of args """
        # for now we will just ignore opts that we don't understand
        tokens = inStr.split()
        opts = []
        args = []
        for t in tokens:
            if t.startswith('--'):
                # interpret as a word opt
                opts.append(t[2:])
            elif t.startswith('-'):
                # interpret as a sequence of single-letter opts
                opts.extend(list(t)[1:])
            else:
                # interpret as an arg
                args.append(t)
        return (opts, args)
    _parse_inStr = staticmethod(_parse_inStr)


    def emptyline(self):
        pass

    def do_EOF(self, inStr=''):
        print >> self.stdout; return True
    def do_exit(self, *foo):
        return True
    do_q = do_quit = do_exit

    def _domain_cmp(x, y):
        """

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
    _domain_cmp = staticmethod(_domain_cmp)


    def _available_websites():
        """ return a list of ids of available websites;
        website ids are of the form codename@hostname:port """

        # in our tests we stub this out rather than actually instantiating an
        #  http server

        # get our hostnames from /etc/hosts
        etc_hosts = file('/etc/hosts')
        hosts = etc_hosts.read()
        etc_hosts.close()

        hostnames = []
        for line in hosts.split('\n'):
            # we were using linesep to split but were getting bad data
            # -- sorry, not enough info, holdover from Cheeze
            line = line.replace('\r','').strip()
            if line == '' or line.startswith('#'):
                continue
            elif not line.count(' ') > 0 and \
                 not line.count('\t') > 0:
                raise PorterError, "Couldn't parse this line in your " \
                                 + "etc/hosts file: %s" % line
            else:
                # line is parseable
                try:
                    ip, domains = [foo.strip() for foo in line.split(None,1)]
                except:
                    raise PorterError, "Couldn't parse this line in your " \
                                     + "etc/hosts file: %s" % line
                hostnames.extend([d.strip() for d in domains.split(' ') \
                                             if d != ''])

        # now get available websites from each host
        #  and populate an index of servers
        servers = {}
        websites = {}

        sys.stdout.write("Polling %s hosts for websites ... " % len(hostnames))
        i = 1; good_servers = 0

        for hostname in hostnames[:1]:
            # loop through candidate hostnames, fail silently if we can't
            #  connect or if the host is serving something other than Fellow/0.2
            #  on port 8000

            sys.stdout.write(str(i) + ' ')
            sys.stdout.flush()
            if i == len(hostnames):
                print "... done."
            i += 1

            # first ping to see if the host is there at all
            ping = Popen3('ping -c1 -t1 -q %s' % hostname).wait()
            if ping != 0:
                servers[hostname] = (0,'no ping')
                continue

            # try to connect on port 8000
            try:
                http = httplib.HTTPConnection(hostname,8000)
                http.connect()
            except socket.error:
                servers[hostname] = (0,'no 8000')
                continue

            # issue our request
            http.request('GET','/')
            response = http.getresponse()
            http.close()

            # process the response
            if not response.getheader('Server').startswith('Fellow/0.2'):
                servers[hostname] = (0,'no fellow')
                continue
            else:
                # this hostname is a Fellow that we can understand!
                good_servers += 1
                new_sites = loads(b64decode(response.read()))
                j = 0
                for site in new_sites:
                    if websites.get(site) is not None:
                        #raise PorterError, "duplicate website id"
                        print 'dupe'
                    else:
                        websites[site] = new_sites[site]
                        j += 1
                servers[hostname] = (j,'live')

        print "We found %s websites on %s servers." % (len(websites), good_servers)

        return servers, websites
    _available_websites = staticmethod(_available_websites)