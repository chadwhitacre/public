from cmd import Cmd

class PorterCmd(Cmd):

    def __init__(self):
        self.intro = 'here we go ...'
        self.prompt = 'porter> '

        # we keep two indexes
        self.domains  = {} # one-to-one mapping of domains to websites
        self.websites = {} # one-to-many mapping of websites to domains

        Cmd.__init__(self)

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

    def do_ls(self, inStr=''): self.do_list(inStr) # alias
    def do_list(self, inStr=''):
        """ print out a list of the domains we are managing """
        # eventually we want to mimic the columns we get from shell ls
        for d in self.domains:
            print d

    def do_add(self, inStr=''): self.do_map(inStr) # alias
    def do_map(self, inStr=''):
        """ given a domain name and a website, map them """
        args = self.parse_inStr(inStr)
        if len(args) < 2:
            print "We need both a domain name and a website id"
            return
        domain, website = args
        print domain, website
        self.domains[domain] = website
        if website in self.websites:
            self.websites[website].append(domain)
        else:
            self.websites[website] = [domain]

    def do_rm(self, inStr=''): self.do_remove(inStr) # alias
    def do_remove(self, inStr=''):
        """ given a domain name, remove it from our mapping """
        domain = self.parse_inStr(inStr)[:1]
        if domain in self.domains:
            self.domains.remove()




