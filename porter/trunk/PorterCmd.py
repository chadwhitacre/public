import os, dbm
from cmd import Cmd

class PorterCmd(Cmd):

    def __init__(self, db_path, *args, **kw):
        self.intro = """
#-------------------------------------------------------------------#
#  Porter v0.1 (c)2004 Zeta Design & Development <www.zetaweb.com>  #
#-------------------------------------------------------------------#
        """
        self.prompt = 'porter> '

        # on startup, read in our data
        #  a one-to-one mapping of domains to websites
        self.db_path = db_path
        db = dbm.open(self.db_path, 'c')
        self.domains = dict(db)
        db.close()

        # filter out www's for our users, they are just for apache
        for domain in self.domains:
            if domain.startswith('www.'):
                del self.domains[domain]

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
        Cmd.__init__(self, *args, **kw)

    def parse_inStr(inStr):
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
    parse_inStr = staticmethod(parse_inStr)

    def emptyline(self):
        pass


    def do_ls(self, inStr=''):
        """ print out a list of the domains we are managing """
        # columnize is undocumented
        opts, args = self.parse_inStr(inStr)
        domains = self.domains.keys()
        if len(domains) > 0: # otherwise columnize gives us "<empty>"

            # massage our list of domains
            domains.sort()
            if args:
                domains = filter(lambda d: d.startswith(args[0]), domains)

            if ('l' in opts) or ('long' in opts):
                header = """
DOMAIN NAME                   SERVER        PORT  ALIASES\n%s""" % (self.ruler*79,)
                print >> self.stdout, header
                for domain in domains:
                    server, portnum = self.domains[domain].split(':')
                    aliases = self.aliases[self.domains[domain]][:]
                    aliases.remove(domain)

                    domain  = domain.ljust(28)[:28]
                    server  = server.ljust(12)[:12]
                    portnum = str(portnum).rjust(4)
                    if aliases: alias = aliases.pop(0)[:28]
                    else:       alias = ''

                    record = "%s  %s  %s  %s" % (domain, server, portnum, alias)

                    print >> self.stdout, record
                    for alias in aliases:
                        print >> self.stdout, ' '*53 + alias
                print >> self.stdout

            else:
                self.columnize(domains, displaywidth=79)

    def complete_ls(self,text, line, begidx, endidx):
        return [d for d in self.domains.keys() if d.startswith(text)]


    def do_map(self, inStr=''): self.do_add(inStr) # alias
    def do_add(self, inStr=''):
        """ given a domain name and a website, map them """

        # get our arguments and validate them
        opts, args = self.parse_inStr(inStr)
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
        website = ':'.join((server,port))

        # update our data
        self.domains[domain] = website
        self.update_db()

        # and update our indices
        if website in self.aliases:
            self.aliases[website].append(domain)
        else:
            self.aliases[website] = [domain]


    def do_rm(self, inStr=''):
        """ given one or more domain names, remove it/them from our storage """
        opts, args = self.parse_inStr(inStr)
        for domain in args:
            if domain in self.domains:
                del self.domains[domain]
            for website in self.aliases:
                if domain in self.aliases[website]:
                    self.aliases[website].remove(domain)
        self.update_db()

    complete_rm = complete_ls

    def do_EOF(self, inStr=''):
        print >> self.stdout; return True

    def update_db(self):
        """ given that our data is clean, store it to file """
        db = dbm.open(self.db_path, 'n')
        for domain in self.domains:
            if domain.startswith('www.'):
                db[domain] = self.domains[domain]
            else:
                db[domain] = self.domains[domain]
                db[domain] = 'www.' + self.domains[domain]
        db.close()
