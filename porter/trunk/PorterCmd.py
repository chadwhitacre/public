import os, dbm
from cmd import Cmd

class PorterCmd(Cmd):

    def __init__(self, db_path, *args, **kw):
        self.intro = 'here we go ...'
        self.prompt = 'porter> '

        # on startup, read in our data
        #  a one-to-one mapping of domains to websites
        self.db_path = db_path
        db = dbm.open(self.db_path, 'c')
        self.domains = dict(db)
        db.close()

        # we also keep an index around
        #  a one-to-many mapping of websites to domains
        self.websites = {}
        for domain in self.domains:
            website = self.domains[domain]
            if website in self.websites:
                self.websites[website].append(domain)
            else:
                self.websites[website] = [domain]

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

    def do_ls(self, inStr=''): self.do_list(inStr) # alias
    def do_list(self, inStr=''):
        """ print out a list of the domains we are managing """
        # columnize is undocumented
        items = self.domains.keys()
        if len(items) > 0: # otherwise columnize gives us "<empty>"
            items.sort()
            self.columnize(items, displaywidth=79)

    def do_add(self, inStr=''): self.do_map(inStr) # alias
    def do_edit(self, inStr=''): self.do_map(inStr) # alias
    def do_map(self, inStr=''):
        """ given a domain name and a website, map them """

        # get our arguments
        opts, args = self.parse_inStr(inStr)
        if len(args) < 2:
            print >> self.stdout, "We need a domain name and a website id."
            return
        domain, website = args[:2]

        # update our data
        self.domains[domain] = website
        self.update_db()

        # and update our indices
        if website in self.websites:
            self.websites[website].append(domain)
        else:
            self.websites[website] = [domain]

    def do_rm(self, inStr=''): self.do_remove(inStr) # alias
    def do_remove(self, inStr=''):
        """ given one or more domain names, remove it/them from our storage """
        opts, args = self.parse_inStr(inStr)
        for domain in args:
            if domain in self.domains:
                del self.domains[domain]
            for w in self.websites:
                if domain in self.websites[w]:
                    self.websites[w].remove(domain)
        self.update_db()

    def update_db(self):
        """ store our data to file """
        db = dbm.open(self.db_path, 'n')
        for domain in self.domains:
            db[domain] = self.domains[domain]
        db.close()

"""
    ##
    # vhost mgmt
    ##

    def _vhosts_get(self,www=0):
        self._confirm_db()
        data = dbm.open(self.vhost_db,'r')
        output = {}
        for vhost in data.keys():
            server = data[vhost]
            if (vhost[:4]=='www.' and www) or vhost[:4]<>'www.':
                output[vhost]=server
        data.close()
        return output

    def _vhost_delete(self,vhost,www=1):
        self._confirm_db()
        _vhosts_dict = self._vhosts_get(www)
        del(_vhosts_dict[vhost])
        if _vhosts_dict.has_key('www.'+vhost):
            del(_vhosts_dict['www.'+vhost])
        self._vhosts_recreate(_vhosts_dict)

    def _vhosts_update(self,_vhosts_dict,www=1):
        self._confirm_db()
        data = dbm.open(self.vhost_db,'w')
        for vhost,server in _vhosts_dict.items():
            data[vhost]=server
            if www:
               wwwvhost = 'www.'+vhost
               data[wwwvhost]=server
        data.close()
        return 'updated'

    def _vhosts_recreate(self,_vhosts_dict,www=1):
        self._confirm_db(check_db=0)
        data = dbm.open(self.vhost_db,'n')
        for vhost,server in _vhosts_dict.items():
            data[vhost]=server
            if vhost[:4]<>'www.' and www:
                wwwvhost = 'www.'+vhost
                data[wwwvhost]=server
        data.close()
        return 'recreated'

    def _confirm_db(self, check_attr=1, check_db=1, check_dbm_compat=1):
        if check_dbm_compat and not unix:
            raise ImportError, '''Apache management requires support for the
            dbm file format which is currently only available on *nix versions
            of python.'''
        if check_attr and not self.vhost_db:
            raise ValueError, '''In order to access the apache related functions
            of this product you need to input a value for vhost_db under the
            properties tab'''
        if check_db:
            if not os.path.exists(self.vhost_db+'.db'):
                self._vhosts_recreate({})

"""