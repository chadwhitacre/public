import os
from pprint import pformat
from utils import *

try:
    import dbm
    unix = 1
except:
    unix = 0

class ApacheVHostManager:
    """ provides functionality to manage an apache virtual hosting setup """

    def __init__(self):
        pass

    ##
    #
    ##

    def test_func(self):
        return self.domains_info()

    def orphans_handle(self):
        orphan_dict ={}
        for zope in self.orphans_find():
            zope_canonical_name= zope+'.zetaserver.com'
            port = zope.split('_')[-1]
            orphan_dict[zope_canonical_name]=port
        self.update_vhosts(orphan_dict)

    def orphans_find(self):
        orphans =[]
        if self.instance_root:
            zopes = self.zope_ids_list()
            zope_entries = [z[0] for z in self.canonical_names_list()]
            for zope in zopes:
                zope_canonical_name= zope+'.zetaserver.com'
                if not zope_canonical_name in zope_entries:
                    orphans.append(zope)
        return orphans

    def _domain_add(self):
        request = self.REQUEST
        response = request.RESPONSE
        form = request.form
        data = {form['name']:form['zope'].split('_')[-1]}
        self.vhosts_update(data)
        return response.redirect('manage_domains')

    def _domain_remove(self):
        request = self.REQUEST
        response = request.RESPONSE
        form = request.form
        vhost = form['vhost']
        self.vhost_delete(vhost)
        return response.redirect('manage_domains')

    def domains_info(self, troubleshoot=0):
        "populates the domains pt"
        vhosts = self.domains_list()
        index_sort(vhosts,0,compare_domains)
        info = {}

        alias_map= {}
        for domain, port in vhosts:
            domain_list = alias_map.get(port,[])
            domain_list.append(domain)
            alias_map[port]=domain_list

        info['zopes'] = zopes = [(z,z.split('_')[-1]) for z in self.zope_ids_list()]

        zope_map = dict([(zport, zname) for zname, zport in zopes])

        canon_map = dict([(zport, zname+'.zetaserver.com') for zname, zport in zopes])

        domains =[]
        for domain, port in vhosts:
            aliases = alias_map[port][:]
            aliases.remove(domain)
            domain_info = {
                'name':domain,
                'port':port,
                'zope':zope_map[port],
                'canonical':canon_map[port],
                'aliases':aliases,
            }
            domains.append(domain_info)
        info['domains']=domains



        #info['vhosts'] = vhosts
        #
        #info['aliases'] = server_info
        if troubleshoot:
            return pformat(info)
        else:
            return info

    def canonical_names_list(self):
        vhosts = self.get_vhosts().items()
        domains = []
        for vhost in vhosts:
            name, port = vhost
            pattern = '.zetaserver.com'
            if name.count(pattern):
                domains.append(vhost)
        return domains

    def domains_list(self):
        vhosts = self.get_vhosts().items()
        domains = []
        for vhost in vhosts:
            name, port = vhost
            pattern = '.zetaserver.com'
            if not name.count(pattern):
                domains.append(vhost)
        return domains


    def get_vhosts(self,www=0):
        self._confirm_db()
        data = dbm.open(self.vhost_db,'r')
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
        data = dbm.open(self.vhost_db,'w')
        for vhost,server in vhosts_dict.items():
            data[vhost]=server
            if www:
               wwwvhost = 'www.'+vhost
               data[wwwvhost]=server
        data.close()
        return 'updated'

    def recreate_vhosts(self,vhosts_dict,www=1):
        self._confirm_db(check_db=0)
        data = dbm.open(self.vhost_db,'n')
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
        if check_attr and not self.vhost_db:
            raise ValueError, '''In order to access the apache related functions
            of this product you need to input a value for vhost_db under the
            properties tab'''
        if check_db:
            if not os.path.exists(self.vhost_db+'.db'):
                self.recreate_vhosts({})

    # just making it so you can do both object_verb and verb_object
    def vhosts_get(self,*args,**kwargs):
        return self.get_vhosts(*args,**kwargs)
    def vhost_delete(self,*args,**kwargs):
        return self.delete_vhost(*args,**kwargs)
    def vhosts_update(self,*args,**kwargs):
        return self.update_vhosts(*args,**kwargs)
    def vhosts_recreate(self,*args,**kwargs):
        return self.recreate_vhosts(*args,**kwargs)
