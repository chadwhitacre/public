import os
try:
    import dbm
    unix = 1
except:
    unix = 0

class ApacheVHostManager:
    """ provides functionality to manage an apache virtual hosting setup """

    def __init__(self):
        pass

    def test_func(self):
        return self.orphans_find()

    def list_ports(self):
        """ return a list of available ports """
        if vhosting:
            avail_ports = [str(x) for x in range(8010,9000,10)]
            for zope in self.zopes_list():
                if self.port_get(zope) in avail_ports:
                    avail_ports.remove(port)
        else:
            return None


    def orphans_find(self):
        orphans =[]
        if self.instance_root:    
            zopes = self.zopes_list()
            zope_entries = self.canonical_names_list()
            for zope in zopes:
                zope_canonical_name= zope+'.zetaserver.com'
                if not zope_canonical_name in zope_entries:
                    orphans.append(zope)
        return orphans
            

    def domains_info(self, troubleshoot=0):
        #"populates the domains pt"
        #vhosts = self.domains_list()
        #index_sort(vhosts,0,compare_domains)
        #info = {}
        #info['vhosts'] = vhosts
        #server_info = {}
        #for domain, server in vhosts:
        #    domain_list = server_info.get(server,[])
        #    domain_list.append(domain)
        #    server_info[server]=domain_list
        #info['servers'] = server_info
        #if troubleshoot:
        #    print pformat(info)
        #    return printed
        #else:
        #    return info
        #
        pass
        
    def canonical_names_list(self):
        vhosts = self.get_vhosts().items()
        domains = []
        for vhost in vhosts:
            name, port = vhost
            pattern = '0.zetaserver.com'
            if name.count(pattern):
                domains.append(vhost)
        return domains
        
    def domains_list(self):
        vhosts = self.get_vhosts().items()
        domains = []
        for vhost in vhosts:
            name, port = vhost
            pattern = '0.zetaserver.com'
            if not name.count(pattern):
                domains.append(vhost)
        return domains

    
    def get_vhosts(self,www=0):
        self._confirm_db()
        data = dbm.open(self.apache_db,'r')
        output = {}
        for vhost in data.keys():
            server = data[vhost]
            if (vhost[:4]=='www.' and www) or vhost[:4]<>'www.':
                output[vhost]=server
        data.close()
        return output
    
    def delete_vhost(self,vhost,www=1):
        self._confirm_db()
        vhosts_dict = self.get_vhosts(www)
        del(vhosts_dict[vhost])
        if vhosts_dict.has_key('www.'+vhost):
            del(vhosts_dict['www.'+vhost])
        self.recreate_vhosts(vhosts_dict)
    
    def update_vhosts(self,vhosts_dict,www=1):
        self._confirm_db()
        data = dbm.open(self.apache_db,'w')
        for vhost,server in vhosts_dict.items():
            data[vhost]=server
            if www:
               wwwvhost = 'www.'+vhost
               data[wwwvhost]=server
        data.close()
        return 'updated'
    
    def recreate_vhosts(self,vhosts_dict,www=1):
        self._confirm_db(check_db=0)
        data = dbm.open(self.apache_db,'n')
        for vhost,server in vhosts_dict.items():
            data[vhost]=server
            if vhost[:4]<>'www.' and www:
                wwwvhost = 'www.'+vhost
                data[wwwvhost]=server
        data.close()
        return 'recreated'

    def _confirm_db(self, check_attr=1, check_db=1, check_dbm_compat=1):
        if check_dbm_compat and not unix:
            raise ImportError, '''Apache management requires support for the 
            dbm file format which is currently only available on unix versions 
            of python.'''
        if check_attr and not self.apache_db:
            raise ValueError, '''In order to access the apache related functions 
            of this product you need to input a value for apache_db under the 
            properties tab'''
        if check_db:
            if not os.path.exists(self.apache_db):
                self.recreate_vhosts({})
    
    # just making it so you can do both object_verb and verb_object
    def vhosts_get(self,*args,**kwargs):
        self.get_vhosts(*args,**kwargs)
    def vhost_delete(self,*args,**kwargs):
        self.delete_vhost(*args,**kwargs)
    def vhosts_update(self,*args,**kwargs):
        self.update_vhosts(*args,**kwargs)
    def vhosts_recreate(self,*args,**kwargs):
        self.recreate_vhosts(*args,**kwargs)
    