try:
    from Products.Cheeze.vh_utils import update_vhosts, \
                                         recreate_vhosts, \
                                         get_vhosts
    vhosting = 1
except:
    # we are not on unix :/
    vhosting = 0
#from Products.ZetaUtils import compare_domains, pformat, index_sort
from AccessControl import ClassSecurityInfo

from Acquisition import Implicit
from Globals import Persistent
from AccessControl.Role import RoleManager
from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import Item

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import DTMLFile, ImageFile
import os
from os.path import join


from CheezeError import CheezeError
from ZopeManager import ZopeManager
from ApacheVHostManager import ApacheVHostManager
from DNSManager import DNSManager


from pprint import pformat as Ipformat

class BigCheeze(Implicit, Persistent, \
                PropertyManager, Item, \
                ZopeManager, DNSManager, ApacheVHostManager):


    security = ClassSecurityInfo()

    id = 'Cheeze'
    title = 'Cheap Zopes :-)'
    meta_type= 'Big Cheeze'

    instance_root = skel_root = vhost_db = dns_file = port_range = ''
    production_mode=0
    
    vhosting = 0

    BigCheeze_manage_options = (
        {'label':'Zopes',           'action':'manage_zopes',    },
        {'label':'Domains',         'action':'manage_domains',  },
        {'label':'Documentation',   'action':'manage_doc',      },
                                )

    manage_options = BigCheeze_manage_options \
                   + PropertyManager.manage_options \
                   + RoleManager.manage_options \
                   + Item.manage_options

    _properties=(
        {'id'   :'title',        'type' :'string','value':'','mode': 'w',},
        {'id'   :'production_mode',        'type' :'boolean','value':0,'mode': 'w',},
        {'id'   :'instance_root','type' :'string','value':'','mode': 'w',},
        {'id'   :'skel_root',    'type' :'string','value':'','mode': 'w',},
        {'id'   :'vhost_db',     'type' :'string','value':'','mode': 'w',},
        {'id'   :'dns_file',     'type' :'string','value':'','mode': 'w',},
        {'id'   :'port_range',   'type' :'string','value':'','mode': 'w',},
                )

    def __init__(self, id):
        self.id = str(id)

    ##
    #   temp
    ##
    def pformat(self,object):
        return Ipformat(object)
    
    
    ##
    # documentation
    ##

    dependencies = DTMLFile('doc/dependencies.txt',globals())

    manage_doc = PageTemplateFile('www/manage_doc.pt',globals())

    style_doc  = DTMLFile('www/style_doc.css',globals())

    def explain(self):
        """  """
        return 'Cheap Zopes :-)'


    ##
    # Zope mgmt
    ##

    manage_zopes = PageTemplateFile('www/manage_zopes.pt',globals())
    
    def zope_info(self):
        info = {}
        zopes = []
        orphans=0
        for zope_id in self.zope_ids_list():
            name, port = self.zope_info_get(zope_id)
            zope_info = {
                'name':name,
                'port':port,
                'id':zope_id,
                'canonical':zope_id+'.zetaserver.com',
            }
            zopes.append(zope_info)
        info['zopes'] = zopes
        return info

    security.declareProtected('Manage Big Cheeze', 'zope_add'),
    def zope_add(self):
        """ add a zope instance """
        if self.instance_root: ZopeManager._zope_create(self)
        return self.REQUEST.RESPONSE.redirect('manage')

    security.declareProtected('Manage Big Cheeze', 'zope_edit'),
    def zope_edit(self, old_name, new_name, old_port, new_port):
        """ edit a zope instance """
        if self.production_mode:
            raise CheezeError, 'Cannot edit instances in production mode'
        old_zope_id = self._zope_id_make(old_name, old_port)
        new_zope_id = self._zope_id_make(new_name, new_port)

        if old_zope_id != new_zope_id:
            self._zope_id_set(old_zope_id, new_zope_id)
        if old_port != new_port:
            self._port_set(new_zope_id, old_port)
        return self.REQUEST.RESPONSE.redirect('manage')

    security.declareProtected('Manage Big Cheeze', 'zope_remove'),
    def zope_remove(self, zope_id):
        """ remove a zope instance """
        self._zope_delete(zope_id)
        return self.REQUEST.RESPONSE.redirect('manage')


    ##
    # Domain mgmt
    ##

    manage_domains = PageTemplateFile('www/manage_domains.pt',globals())
    def domains_info(self, troubleshoot=0):
        """ populates the domains pt """
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
            try:
                aliases = alias_map[port][:]
                aliases.remove(domain)
                domain_info = {
                    'name':domain,
                    'port':port,
                    'zope':zope_map[port],
                    'canonical':canon_map[port],
                    'aliases':aliases,
                }
                
            except KeyError:
                domain_info = {
                    'name':domain,
                    'port':port,
                    'zope':'ORPHANED',
                    'canonical':'',
                    'aliases':[],
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
            
    def domain_add(self):
        """handles adding domains"""
        if self.vhost_db: return ApacheVHostManager._domain_add(self)

    def domain_edit(self):
        """ add a domain instance """
        pass

    def domain_remove(self):
        """handles removing domains"""
        if self.vhost_db: return ApacheVHostManager._domain_remove(self)




    ##
    # helper routines
    ##

    def _setPropValue(self, id, value):
        """ intercept from PropertyManager so we can do validation """
        if   id == 'instance_root':
            self._set_instance_root(value)
        elif id == 'skel_root':
            self._set_skel_root(value)
        elif id == 'vhost_db':
            self._set_vhost_db(value)
        elif id == 'port_range':
            self._set_port_range(value)
        else:
            PropertyManager._setPropValue(self, id, value)

    def _set_instance_root(self, instance_root):
        """ validate and set the instance root """
        if instance_root == '':
            PropertyManager._setPropValue(self, 'instance_root', '')
        elif not os.path.exists(instance_root):
            raise CheezeError, "Proposed instance root " \
                             + "'%s' does not exist" % instance_root
        elif not os.path.isdir(instance_root):
            raise CheezeError, "Proposed instance root " \
                             + "'%s' " % instance_root \
                             + "does not point to a directory"
        else:
            clean_path = self._scrub_path(instance_root)
            PropertyManager._setPropValue(self,
                                          'instance_root',
                                          clean_path)

    def _set_skel_root(self, skel_root):
        """ validate and set the skel root """
        if skel_root == '':
            PropertyManager._setPropValue(self, 'skel_root', '')
        elif not os.path.exists(skel_root):
            raise CheezeError, "Proposed skel root " \
                             + "'%s' does not exist" % skel_root
        elif not os.path.isdir(skel_root):
            raise CheezeError, "Proposed skel root '%s' " % skel_root \
                             + "does not point to a directory"
        else:
            clean_path = self._scrub_path(skel_root)
            PropertyManager._setPropValue(self, 'skel_root', clean_path)

    def _set_port_range(self, port_range):
        if port_range == '':
            PropertyManager._setPropValue(self, 'port_range', '')
        else:
            self._ports_list(port_range) # smoke it!
            PropertyManager._setPropValue(self, 'port_range', port_range)

    def _set_vhost_db(self, vhost_db):
        """ validate and set the vhost db"""
        from whichdb import whichdb
        if vhost_db == '':
            PropertyManager._setPropValue(self, 'vhost_db', '')
        elif whichdb(vhost_db) is None or whichdb(vhost_db) == '':
            raise CheezeError, "vhost_db must point to a valid dbm file"
        else:
            clean_path = self._scrub_path(vhost_db)
            PropertyManager._setPropValue(self, 'vhost_db', clean_path)


    def _scrub_path(self, p):
        """ given a valid path, return a clean path """
        p = os.path.normpath(p)
        p = os.path.normcase(p)
        return p


    ##
    # presentation helpers
    ##

    style           = DTMLFile('www/style.css',globals())

    image_delete    = ImageFile('www/delete.png',globals(),)

    image_save      = ImageFile('www/save.png',globals(),)

    image_zopes     = ImageFile('www/zopes.png',globals(),)

    manage = manage_main = manage_zopes



##
# Product addition and registration
##

manage_add = PageTemplateFile('www/manage_add.pt', globals())

def manage_addBigCheeze(self, id, REQUEST=None):
    """  """
    self._setObject(id, BigCheeze(id))

    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

def initialize(context):
    context.registerClass(
        BigCheeze,
        permission='Add Big Cheeze',
        constructors=(manage_add, manage_addBigCheeze),
        icon='www/big_cheeze.png',
        )
