"""

Porter is our Cmd app that manages rewrite.db and our named.porter.conf:

    rewrite.db -- {'domain':'server:port'}

    named.porter.conf -- fragment to be appended to named.conf, records are of the
    form:

        zone "example.com" {
                type master;
                file "porter.zone";
        };

    The good news here is that all we need to replace is example.com. So it
    really shouldn't be too much overhead to just generate this entire file
    fragment every time we store to disk. And the rest of the record can be
    hard-coded, so we run very little chance of screwing this up. ;^)

On program initialization, we read data in from rewrite.db into an internal
data structure, and we generate an index that we use to present aliases for
convenience. Then whenever we do one of [mk, rm] we want to save these changes
to the db and regenerate our named.porter.conf file.

"""

import os, dbm, cmd, shutil, sys
from os.path import join, abspath, isfile, isabs
from StringIO import StringIO

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
        self.conf_path = join(self.var, "named.porter.conf")

        # read in data from our db, which is a one-to-one mapping of domains
        #  to websites (website == server:port)
        db = dbm.open(self.db_path, 'c')
        domains = dict(db)
        db.close()

        # should we do some integrity checking here? i.e., make sure that all
        # domains have a www counterpart? check for dupes?

        # filter out www's for our users, we will add them back in when we
        #  write to disk
        self.domains = {}
        for domain in domains:
            if not domain.startswith('www.'):
                self.domains[domain] = domains[domain]

        # we also keep an index around
        #  a one-to-many mapping of websites to domains
        self.aliases = {}
        for domain in self.domains:
            website = self.domains[domain]
            if website in self.aliases:
                self.aliases[website].append(domain)
            else:
                self.aliases[website] = [domain]

        # and let our superclass have its way too
        cmd.Cmd.__init__(self, *args, **kw)

        # ui settings
        self.intro = """
#-------------------------------------------------------------------#
#  Porter v0.1 (c)2004 Zeta Design & Development <www.zetaweb.com>  #
#-------------------------------------------------------------------#

You are currently managing %s domains. Type ? for help.
        """ % len(self.domains)
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
          OPTIONS: -l/--long, -i/--info, -r/--raw
          ARGS: With the -l option or with no options, ls takes an optional
                argument. If you pass in this argument, Porter only lists 
                domains that begin with that value. So for example, 'ls zeta' 
                would list zetaweb.com and zetaserver.com, but not 
                sub1.zetaweb.com nor zogurt.org.

    mk -- register a domain with Porter
          ARGS: domain server port, e.g.: example.com srvrname 8080
          ALIASES: add, mv. mv adds tab-completion for domain names

    rm -- unregister a domain
          ARGS: one or more space-separated domain names, e.g.: foo.example.net
          domain names can be tab completed 
            """

    ##
    # Completes
    ##

    def complete_domains(self, text, line, begidx, endidx):
        return [d for d in self.domains.keys() if d.startswith(text)]


    ##
    # Create/Update
    ##

    complete_mv = complete_domains

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

    complete_ls = complete_domains

    def do_ls(self, inStr=''):
        """ print out a list of the domains we are managing """
        opts, args = self._parse_inStr(inStr)
        domains = self.domains.keys()
        if ('i' in opts) or ('info' in opts):
            print >> self.stdout, "You are currently managing %s domains." % len(self.domains)
            return
        if len(domains) > 0: # otherwise columnize gives us "<empty>"

            # TODO: this might be big enough to refactor into dict switch notation

            if ('r' in opts) or ('raw' in opts):
                print >> self.stdout, """
KEY                           VALUE\n%s""" % (self.ruler*60,)
                raw = dbm.open(self.db_path,'r')
                for key in dict(raw):
                    print >> self.stdout, "%s  %s" % (key.ljust(28), raw[key].ljust(28))
                print >> self.stdout
                raw.close()
            else:
                # massage our list of domains
                domains.sort(self._domain_cmp)
                if args:
                    domains = filter(lambda d: d.startswith(args[0]), domains)

                if ('l' in opts) or ('long' in opts):
                    header = """
DOMAIN NAME                   SERVER        PORT  ALIASES\n%s""" % (self.ruler*79,)
                    print >> self.stdout, header
                    for domain in domains:
                        server, portnum = self.domains[domain].split(':')
                        aliases = self.aliases[self.domains[domain]][:]
                        aliases.remove(domain) # don't list ourselves in aliases

                        domain  = domain.ljust(28)[:28]
                        server  = server.ljust(12)[:12]
                        portnum = str(portnum).rjust(4)
                        if aliases: alias = aliases.pop(0)[:28]
                        else:       alias = ''

                        record = "%s  %s  %s  %s" % (domain, server, portnum, alias)

                        print >> self.stdout, record
                        for alias in aliases:
                            print >> self.stdout, ' '*50 + alias
                    print >> self.stdout

                else:
                    # columnize is an undocumented method in cmd.py
                    self.columnize(domains, displaywidth=79)


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

    def _write_to_disk(self):
        """ given that our data is clean, store it to disk """

        # first step is to back up the current files
        shutil.copyfile(self.db_path + '.db', self.db_path + '.db.old')
        if isfile(self.conf_path):
            shutil.copyfile(self.conf_path, self.conf_path + '.old')

        # create a local copy of self.domains, adding www's back in
        #  we create separate record structs so that we can sort the one that
        #  goes to named.porter.conf, thus making testing easier
        db_records = {}; conf_records = []
        for domain in self.domains:
            website = self.domains[domain]
            db_records[domain] = website
            db_records['www.' + domain] = website
        conf_records = db_records.keys()
        conf_records.sort(self._domain_cmp)

        # now first write our db file
        db = dbm.open(self.db_path, 'n')
        for domain in db_records:
            db[domain] = db_records[domain]
        db.close()

        # then generate our named.conf fragment
        #  we generate the text before actually writing, just to be safe
        tmp = StringIO()
        print >> tmp, "\n// begin records generated by porter\n"
        record="""\
zone "%s" {
        type master;
        file "porter.zone";
};\n"""
        for domain in conf_records:
            print >> tmp, record % domain
        print >> tmp, "\n// end records generated by porter"
        named_porter_conf = tmp.getvalue()
        tmp.close()

        # so we could do some integrity checking in here if we wanted to
        #print named_porter_conf

        frag = file(self.conf_path,'w+')
        frag.write(named_porter_conf)
        frag.close()


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

        Domains should be at least two places long, i.e, example.com, not example

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
