import os
from pprint import pformat
from utils import *
from CheezeError import CheezeError

try:
    import dbm
    unix = 1
except:
    unix = 0

class ApacheVHostManager:
    """ provides functionality to manage an apache virtual hosting setup """

    ##
    # info providers - these can be used in mgmt zpt's
    ##
    
    def canonical_names_list(self):
        vhosts = self._vhosts_get().items()
        domains = []
        for vhost in vhosts:
            name, port = vhost
            pattern = '.zetaserver.com'
            if name.count(pattern):
                domains.append(vhost)
        return domains

    def domains_list(self):
        vhosts = self._vhosts_get().items()
        domains = []
        for vhost in vhosts:
            name, port = vhost
            pattern = '.zetaserver.com'
            if not name.count(pattern):
                domains.append(vhost)
        return domains
        
    ##
    # heavy lifters - these are only used by BigCheeze wrappers
    ##

    def _zope_add(self):
        form = self.REQUEST.form
        name = form['name']
        port = str(form['port'])
        canonical = '%s_%s.zetaserver.com'%(name,port)
        data = {canonical:port}
        self._vhosts_update(data)
    
    def _zope_edit(self):
        form = self.REQUEST.form
        old_name = form['old_name']
        old_port = form['old_port']
        old_canonical = '%s_%s.zetaserver.com'%(old_name,old_port)
        new_name = form['new_name']
        new_port = str(form['new_port'])
        new_canonical = '%s_%s.zetaserver.com'%(new_name,new_port)
        data = self._vhosts_get()
        del(data[old_canonical])
        data[new_canonical]=new_port
        self._vhosts_recreate(data)

    def _zope_remove(self):
        form = self.REQUEST.form
        canonical = form['zope_id']+'.zetaserver.com'
        self._vhost_delete(canonical)


    def _domain_add(self):
        request = self.REQUEST
        response = request.RESPONSE
        form = request.form
        data = {form['name']:form['zope'].split('_')[-1]}
        self._vhosts_update(data)

    def _domain_edit(self):
        form= self.REQUEST.form
        old_name = form['old_name']
        new_port = form['new_port']
        data = {old_name:new_port}
        self._vhosts_update(data)

    def _domain_remove(self):
        request = self.REQUEST
        response = request.RESPONSE
        form = request.form
        vhost = form['vhost']
        self._vhost_delete(vhost)

    ###
    # Used to keep the dbm file in sync with the filesystem
    ###
    
    def fs_db_sync(self):
        orphans, leftovers = self.fs_db_sync_info()
        orphan_dict ={}
        for zope in orphans:
            zope_canonical_name= zope+'.zetaserver.com'
            port = zope.split('_')[-1]
            orphan_dict[zope_canonical_name]=port
        self._vhosts_update(orphan_dict)
        for leftover in leftovers:
            self._vhost_delete(leftover)

    def fs_db_sync_info(self):
        orphans =[]
        leftovers=[]
        if self.instance_root:
            # these are actually existing instances
            zopes = self.zope_ids_list()
            # these are all the instances in the db
            zope_entries = [z[0] for z in self.canonical_names_list()]
            
            
            # becuase the storage of instances is actually the filesystem, we 
            # need to sync the db with the fs
            for zope in zopes:
                zope_canonical_name= zope+'.zetaserver.com'
                if not zope_canonical_name in zope_entries:
                    orphans.append(zope)
                else:
                    zope_entries.remove(zope_canonical_name)
            leftovers = zope_entries
        return (orphans,leftovers)


    ##
    # helpers
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
    vhosts_get = _vhosts_get
    
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


