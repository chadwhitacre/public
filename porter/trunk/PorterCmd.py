from cmd import Cmd

class PorterCmd(Cmd):

    def __init__(self):
        self.prompt = 'porter> '
        self.domains = ['zetaweb.com'
                       ,'thedwarf.com'
                       ,'malcontents.org'
                       ,'jewelryjohn.com'
                       ,'tesm.edu'
                        ]
        self.domains.sort()
        Cmd.__init__(self)

    def parseopts(arg):
        """ given a Cmd arg string, return a list of options """
        tokens = arg.split()
        opts = []
        for t in tokens:
            if t.startswith('---'):
                continue
            elif t.startswith('--'):
                opts.append(t[2:])
            elif t.startswith('-'):
                opts.extend(list(t)[1:])
            else:
                opts.extend(list(t))
        return opts
    parseopts = staticmethod(parseopts)

    def emptyline(self):
        pass

    def do_ls(self, arg=''):
        """ print out a list of the domains we are managing """
        opts = self.parseopts(arg)
        print opts
        if not arg:
            arg = 'domains'
        for d in self.domains:
            print d

