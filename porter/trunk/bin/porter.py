#!/usr/bin/env python
"""Porter is a Cmd app that manages rewrite.db.

On program initialization, we read data in from rewrite.db into an internal data
structure, and we generate an index that we use to present aliases for
convenience. Then whenever we do one of [mk, rm] we want to save our changes to
the db.

"""

import cmd
import datetime
import dbm
import os
import shutil
import sys


__version__ = '0.2'


class PorterError(RuntimeError):
    """ error class for porter """
    pass


class Porter(cmd.Cmd):

    def __init__(self, db_path, stdout=None):
        """
        """
        stdout = stdout or sys.stdout
        cmd.Cmd.__init__(self, stdout=stdout)
        if db_path.endswith('.db'):
            db_path = db_path[:-3]
        self.db_path = db_path


        # Read our data from storage into self.domains.
        # =============================================
        # We also populate the indices self.aliases and self.servers in this
        # method.

        self._read_from_disk()


        # Set some UI variables.
        # ======================

        year = datetime.date.today().year
        num = len(self.domains)
        word = (num == 1) and 'domain' or 'domains'

        self.intro = """
#------------------------------------------------------------------------#
#  Porter v0.2 (c)2004-%s Zeta Design & Development <www.zetaweb.com>  #
#------------------------------------------------------------------------#

You are currently managing %s %s. Type ? for help.
        """ % (year, num, word)
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
          OPTIONS: -l/--long, -i/--info, -r/--raw, -s/--server
          ARGS: ls takes an optional argument, a prefix by which to constrain
                based on domain name (if -l or no options are given), or based
                on server name (if -s is given). So for example, 'ls zeta'
                would list zetaweb.com and zetaserver.com, but not zogurt.org
                nor sub1.zetaweb.com. If -s is given, results are sorted by
                server and port number, otherwise by domain name.
          Domains (or servers with -s) can be tab-completed.

    mk -- register a domain
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

    def complete_domains(self, text, line, begidx, endidx):
        return [d for d in self.domains.keys() if d.startswith(text)]

    def complete_domains_or_servers(self, text, line, begidx, endidx):
        opts, args = self._parse_inStr(line)
        if ('s' in opts) or ('server' in opts):
            return [i[0] for i in self.aliases if i[0].startswith(text)]
        else:
            return [d for d in self.domains if d.startswith(text)]


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
        """Given a domain name and a website, map them.
        """

        # Get arguments and validate them.
        # ================================

        opts, args = self._parse_inStr(inStr)
        if len(args) < 3:
            print >> self.stdout, "We need a domain name, a server name, " +\
                                  "and a port number."
            return
        domain, server, port = args[:3]
        if len(domain.split('.')) < 2:
            print >> self.stdout, "'%s' does not look like a complete domain." % domain
            return
        if domain.startswith('www.'):
            print >> self.stdout, "Please do not include 'www' on domains."
            return
        # not worth validating port number since it will come from "dropdown" anyway
        # not worth validating server since it will come from "dropdown" anyway

        old_website = self.domains.get(domain, None)
        new_website = ':'.join((server, port))
        new_index = (server, int(port))


        # Update database.
        # ================

        self.domains[domain] = new_website
        self._write_to_disk()


        # Update indices.
        # ===============

        if old_website is not None:
            server, port = old_website.split(':')
            old_index = (server, int(port))
            self.aliases[old_index].remove(domain)

        if new_index in self.aliases:
            if domain not in self.aliases[new_index]:
                self.aliases[new_index].append(domain)
        else:
            self.aliases[new_index] = [domain]
        self.aliases[new_index].sort(self._domain_cmp)


    ##
    # Read
    ##

    complete_l = complete_ls = complete_domains_or_servers

    def do_ls(self, inStr=''):
        """Print out a list of the domains we are managing.
        """

        out = ['']
        opts, args = self._parse_inStr(inStr)
        domains = self.domains.keys()


        # Display summary info.
        # =====================

        if ('i' in opts) or ('info' in opts):
            num = len(self.domains)
            word = (num == 1) and 'domain' or 'domains'
            out.append("You are currently managing %s %s." % (num, word))


        # Display raw details.
        # ====================

        elif ('r' in opts) or ('raw' in opts):
            out.append("KEY" + (" " * 27) + "VALUE")
            out.append(self.ruler*60)
            raw = dbm.open(self.db_path,'r')
            for key in dict(raw):
                out.append("%s  %s" % (key.ljust(28), raw[key].ljust(28)))
            out.append('')
            raw.close()


        # Display more user-friendly details.
        # ===================================

        else:

            # Massage our list of domains.
            # ============================

            filt = args and args[0] or ''

            if ('s' in opts) or ('server' in opts):
                domains = []
                for server, port in sorted(self.aliases):
                    if filt and not server.startswith(filt):
                        continue
                    domains.extend(self.aliases[(server, port)])
            else:
                domains.sort(self._domain_cmp)
                if filt:
                    domains = [d for d in domains if d.startswith(filt)]


            # Nothing to show.
            # ================
            # If we handle this case in the next clause, columnize prints
            # "<empty>."

            if len(domains) == 0:
                pass


            # Output in long format.
            # ======================

            elif ('l' in opts) or ('long' in opts):

                out.append( "DOMAIN NAME" + (' '*19)
                          + "SERVER" + (' '*8)
                          + "PORT" + '  '
                          + "ALIASES"
                           )
                out.append(self.ruler*79)

                curserver = ''
                for domain in domains:

                    server, port = self.domains[domain].split(':')
                    if server != curserver: # insert rules in -s mode
                        if curserver:
                            out.append('-'*79)
                        curserver = server
                    index = (server, int(port))
                    aliases = self.aliases[index][:]
                    aliases.remove(domain)

                    domain  = domain.ljust(28)[:28]
                    server  = server.ljust(12)[:12]
                    port = port.rjust(4)
                    if aliases:
                        alias = aliases.pop(0)[:28]
                    else:
                        alias = ''

                    out.append('  '.join([domain, server, port, alias]))

                    for alias in aliases:
                        out.append(' '*50 + alias)

                out.append('')


            # Output in short format.
            # =======================
            # I hardly ever use this. Should it even be here?

            else:
                # columnize is an undocumented method in cmd.py
                self.columnize(domains, displaywidth=79)

        print >> self.stdout, '\n'.join(out)

    def do_l(self, inStr=''):
        """ alias for ls -l """
        self.do_ls('-l ' + inStr)


    ##
    # Delete
    ##

    complete_rm = complete_domains

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

    def _read_from_disk(self):
        """Read data in from storage, index it, and store it.
        """

        # Read in data from our db.
        # =========================
        # The database is a one-to-one mapping of domains to websites,
        # where 'website' means 'server:port'.

        db = dbm.open(self.db_path, 'c') # 'c' means create it if not there
        rawdata = dict(db)
        db.close()

        # should we do some integrity checking here? i.e., make sure that all
        # domains have a www counterpart? check for dupes?


        # Filter out www's for better usability.
        # ======================================
        # We will add them back in when we write to disk.

        domains = {}
        for domain in rawdata:
            if len(domain.split('.')) < 2:
                continue
            if not domain.startswith('www.'):
                domains[domain] = rawdata[domain]


        # Index the data.
        # ===============
        # This is a one-to-many mapping of (server, port) tuples to domains.

        aliases = {}
        for domain in sorted(domains, self._domain_cmp):
            server, port = domains[domain].split(':')
            index = (server, int(port))
            if index in aliases:
                aliases[index].append(domain)
            else:
                aliases[index] = [domain]


        # Store it.
        # =========

        self.domains = domains.copy()
        self.aliases = aliases.copy()


    def _write_to_disk(self):
        """Given clean data in self.domains, store it to disk.
        """

        # Create a local copy of self.domains.
        # ====================================
        # This is where we add www aliases back in.

        db_records = {}
        for domain in self.domains:
            website = self.domains[domain]
            db_records[domain] = website
            db_records['www.' + domain] = website


        # Back up the current file and write the new one.
        # ===============================================

        shutil.copyfile(self.db_path + '.db', self.db_path + '.db.old')
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



def main(argv=None):
    """
    """

    if argv is None:
        argv = sys.argv


    # Determine the data file we are managing.
    # ========================================

    arg = argv[1:2]
    if arg:
        db_path = arg[0]
    else:
        db_path = os.environ.get('PORTER_DB', None)
        if db_path is None:
            print >> sys.stderr, "No dbm file specified."
            raise SystemExit()
    dp_path = os.path.realpath(db_path)
    if not os.path.isfile(db_path):
        if not os.path.isfile(db_path+'.db'):
            print "Attempt to create new database at:\n  %s." % dp_path


    # Run a command or enter interactive mode.
    # ========================================

    porter = Porter(db_path)
    command = ' '.join(argv[2:])
    if command:
        porter.onecmd(command)
    else:
        try:
            porter.cmdloop()
        except KeyboardInterrupt:
            porter.onecmd("EOF")


if __name__ == '__main__':
    main(sys.argv)
