"""

Binder is a utility to safely manage a list of domain names for which DNS is to
be provided by a BIND 8 server. Binder assumes that all domains will share the
same SOA, MX records, and other configuration. This shared information is
expected to be in a zone file at namesrvr:/etc/namedb/binder.zone. We store our
list of domains as a pickle in a dat file, and whenever we update this list we
poop out two fragments for inclusion in a named.conf file:

    named.binder.master.conf -- fragment to be included in named.conf on the
    master DNS server; records are of the form:

        zone "example.com" {
                type master;
                file "binder.zone";
        };

    named.binder.slave.conf -- fragment to be included in named.conf on the
    slave DNS server; records are of the form:

        zone "example.com" {
                type slave;
                file "binder.zone";
        };

"""

import cmd, datetime, os, pickle, shutil, sys
from os.path import join, isfile
from StringIO import StringIO

class BinderError(RuntimeError):
    """ error class for binder """
    pass

class Binder(cmd.Cmd):

    def __init__(self, *args, **kw):

        # set our data and output paths
        PKG_HOME = os.environ.get('PKG_HOME', sys.path[0])
        INSTANCE_HOME = os.environ.get('INSTANCE_HOME', PKG_HOME)
        OUTPUT_PATH = os.environ.get('OUTPUT_PATH', PKG_HOME)

        self.var = join(INSTANCE_HOME, 'var')
        self.dat_path = join(self.var, 'binder.dat')
        self.output_path = OUTPUT_PATH

        # read in our data from storage
        self.domains = self._read_from_disk()

        # should we do some integrity checking here? i.e., make sure that all
        # domains are only two parts long? check for dupes?

        # and let our superclass have its way too
        cmd.Cmd.__init__(self, *args, **kw)

        # ui settings
        year = datetime.date.today().year
        num = len(self.domains)
        if num == 1: word = 'domain'
        if num <> 1: word = 'domains'

        self.intro = """
#-------------------------------------------------------------------------#
#  Binder v0.1 (c) 2004-%s Zeta Design & Development <www.zetaweb.com>  #
#-------------------------------------------------------------------------#

You are currently managing %s %s. Type ? for help.
        """ % (year, num, word)
        self.prompt = 'binder> '

    ##
    # UI polish
    ##

    # help
    def do_help(self, bar=""):

        if bar:
            cmd.Cmd.do_help(self, bar)

        else:
            print >> self.stdout, """\

Binder is a utility to safely manage a list of domain names for which DNS is to
be provided by a BIND 8 server.

Commands available:

    ls -- list available domains
          OPTIONS: -i/--info
          ARGS: ls takes an optional argument. If you pass in this argument,
                Binder only lists domains that begin with that value. So for
                example, 'ls zeta' would list zetaweb.com and zetaserver.com,
                but not sub1.zetaweb.com nor zogurt.org.
          Domains can be tab-completed.

    mk -- register a domain with Binder
          ALIAS: add

    rm -- unregister a domain
          ARGS: one or more space-separated domain names, e.g.: example.net
          Domains can be tab-completed.
            """
#    mv -- rename a domain that Binder is managing
#          ALIAS: rename
#          ARGS: two domain names, first one can be tab-completed

    # completes
    def complete_domains(self, text, line, begidx, endidx):
        return [d for d in self.domains if d.startswith(text)]

    # misc.
    def emptyline(self):
        pass

    def do_EOF(self, inStr=''):
        print >> self.stdout; return True
    def do_exit(self, *foo):
        return True
    do_q = do_quit = do_exit


    ##
    # Create/Update
    ##

    def do_add(self, inStr=''):
        """ alias for mk """
        self.do_mk(inStr)

    def do_mk(self, inStr=''):
        """ given a domain name, add it to our list"""

        # get our arguments and validate them
        opts, args = self._parse_inStr(inStr)
        if len(args) < 1:
            print >> self.stdout, "No domain name was provided."
            return
        domain = args[0]
        if domain.count('.') <> 1:
            print >> self.stdout, "The domain name is not of the form: " +\
                                  "example.com."
            return
        if domain in self.domains:
            print >> self.stdout, "We are already managing that domain name."
            return

        # update our data
        self.domains.append(domain)
        self.domains.sort(self._domain_cmp)
        self._write_to_disk()


    ##
    # Read
    ##

    complete_ls = complete_domains

    def do_ls(self, inStr=''):
        """ print out a list of the domains we are managing """
        opts, args = self._parse_inStr(inStr)
        if len(args) > 0:
            filt = args[0]
            domains = [d for d in self.domains if d.startswith(filt)]
        else:
            domains = self.domains

        if ('i' in opts) or ('info' in opts):
            num = len(domains)
            if num == 1: word = 'domain'
            if num <> 1: word = 'domains'
            print >> self.stdout, "We are currently managing " +\
                                  "%s %s." % (num, word)
            return

        if len(domains) > 0: # otherwise columnize gives us "<empty>"

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
                self.domains.remove(domain) # clean data means only one
           else:
                print >> self.stdout, "%s is not in our database." % domain

        self._write_to_disk()


    ##
    # disk interface
    ##

    def _read_from_disk(self):
        """ read data from our data file, and return it"""

        if isfile(self.dat_path):
            dat_file = file(self.dat_path,'r')
            domains = pickle.load(dat_file)
            dat_file.close()
        else:
            # no data yet
            domains = []

        return domains


    def _write_to_disk(self):
        """ given that our data is clean, store it to disk """

        ##
        # dat file
        ##

        # first back up the current file
        if isfile(self.dat_path):
            shutil.copyfile(self.dat_path, self.dat_path + '.old')

        # now write the new one
        dat_file = file(self.dat_path,'w+')
        pickle.dump(self.domains, dat_file
                   ,pickle.HIGHEST_PROTOCOL) # this tells it to use binary format
        dat_file.close()


        ##
        # named frags
        ##

        # generate our 2 named.conf fragments
        for named_type in ('master','slave'):
            #  generate the text before actually writing, just to be safe
            tmp = StringIO()
            print >> tmp, "\n// begin records generated by binder\n"
            record="""\
zone "%s" {
        type %s;
        file "binder.zone";
};\n"""
            for domain in self.domains:
                print >> tmp, record % (domain, named_type)
            print >> tmp, "\n// end records generated by binder"
            named_conf_frag = tmp.getvalue()
            tmp.close()

            # we could do some integrity checking in here if we wanted to
            #print named_conf_frag

            # now write it to disk
            frag_name = "named.binder.%s.conf" % named_type
            frag_path = join(self.output_path, frag_name)
            frag = file(frag_path,'w+')
            frag.write(named_conf_frag)
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
        except: raise BinderError, "unable to parse '%s' as a domain name" % x
        try:    d2 = y.split('.')
        except: raise BinderError, "unable to parse '%s' as a domain name" % y

        # more data checks
        if len(d1) < 2:
            raise BinderError, "'%s' doesn't look like a full domain name" % x
        if len(d2) < 2:
            raise BinderError, "'%s' doesn't look like a full domain name" % y

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
