from cmd import Cmd

class PorterCmd(Cmd):

    def __init__(self, **kw):
        self.intro = 'here we go ...'
        self.prompt = 'porter> '

        # we keep two indexes
        self.domains  = {} # one-to-one mapping of domains to websites
        self.websites = {} # one-to-many mapping of websites to domains

        Cmd.__init__(self, **kw)

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
        # columnize is undocumented
        items = self.domains.keys()
        if len(items) > 0:
            items.sort()
            self.columnize(items, displaywidth=79)

    def do_add(self, inStr=''): self.do_map(inStr) # alias
    def do_edit(self, inStr=''): self.do_map(inStr) # alias
    def do_map(self, inStr=''):
        """ given a domain name and a website, map them """
        opts, args = self.parse_inStr(inStr)
        if len(args) < 2:
            print >> self.stdout, "We need a domain name and a website id."
            return
        domain, website = args[:2]
        self.domains[domain] = website
        if website in self.websites:
            self.websites[website].append(domain)
        else:
            self.websites[website] = [domain]

    def do_rm(self, inStr=''): self.do_remove(inStr) # alias
    def do_remove(self, inStr=''):
        """ given one or more domain names, remove it/them from our indices """
        opts, args = self.parse_inStr(inStr)
        for domain in args:
            if domain in self.domains:
                self.domains.pop(domain)
            for w in self.websites:
                if domain in self.websites[w]:
                    self.websites[w].remove(domain)




