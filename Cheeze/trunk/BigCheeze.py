try:
    from Products.Cheeze.vh_utils import _vhosts_update, \
                                         _vhosts_recreate, \
                                         _vhosts_get
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
from utils import *

class BigCheeze(Implicit, Persistent, \
                PropertyManager, Item, \
                ZopeManager, DNSManager,  ApacheVHostManager):


    security = ClassSecurityInfo()

    id = 'Cheeze'
    title = 'Cheap Zopes :-)'
    meta_type= 'Big Cheeze'

    instance_root = skel_root = vhost_db = dns_file = port_range = port_list=''
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
        {'id'   :'port_list',    'type' :'string','value':'','mode': 'w',},
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
    # A couple of functions to help us figure out how to act
    ##

    def managesInstances(self):
        if self.instance_root:
            return 1
        else:
            return 0
    
    def managesVhosting(self):
        if self.managesVhosting():
            return 1
        else:
            return 0
    
    def mode(self):
        managesInstances = self.managesInstances()
        managesVhosting = self.managesVhosting()
        if not(managesInstances or managesVhosting):
            return 0
        elif managesInstances and not managesVhosting:
            return 1
        elif not managesInstances and managesVhosting:
            return 2
        elif managesInstances and managesVhosting:
            return 3

    def friendly_mode(self):
        friendlies={
        0:'''Just installed''',
        1:'''Manages zope instances''',
        2:'''Manages vhosting db''',
        3:'''Manages zope instances and vhosting db'''
        }
        return friendlies[self.mode()]

    ##
    # Zope mgmt
    ##

    manage_zopes = PageTemplateFile('www/manage_zopes.pt',globals())
        
    security.declareProtected('Manage Big Cheeze', 'zope_add'),
    def zope_add(self):
        """ add a zope instance """
        mode = self.mode()
        if mode in [1,3]:  
            ZopeManager._zope_add(self)
            if mode==3:      
                self.fs_db_sync()
        elif mode==2:
            ApacheVHostManager._zope_add(self)
        return self.REQUEST.RESPONSE.redirect('manage')

    security.declareProtected('Manage Big Cheeze', 'zope_edit'),
    def zope_edit(self):
        """ edit a zope instance """
        if self.production_mode:
            raise CheezeError, 'Cannot edit instances in production mode'
            
        mode = self.mode()
        if mode in [1,3]:  
            ZopeManager._zope_edit(self)
            if mode==3:      
                self.fs_db_sync()
        elif mode==2:
            ApacheVHostManager._zope_edit(self)
        
        return self.REQUEST.RESPONSE.redirect('manage')

    security.declareProtected('Manage Big Cheeze', 'zope_remove'),
    def zope_remove(self):
        """ remove a zope instance """
        mode = self.mode()
        if mode in [1,3]:  
            ZopeManager._zope_remove(self)
            if mode==3:      
                self.fs_db_sync()
        elif mode==2:
            ApacheVHostManager._zope.remove(self)
        return self.REQUEST.RESPONSE.redirect('manage')
    
    def zope_info(self):
        info = {}
        zopes = []
        mode = self.mode()
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


    ##
    # Domain mgmt
    ##

    manage_domains = PageTemplateFile('www/manage_domains.pt',globals())
    
    def domain_add(self):
        """handles adding domains"""
        self._domain_add()
        return self.REQUEST.RESPONSE.redirect('manage_domains')

    def domain_edit(self):
        """ add a domain instance """
        self._domain_edit()
        raise CheezeError, 'domain editing not yet implemented'

    def domain_remove(self):
        """handles removing domains"""
        self._domain_remove()
        return self.REQUEST.RESPONSE.redirect('manage_domains')
        
    def domains_info(self):
        """ populates the domains pt """
        vhosts = self.domains_list()
        index_sort(vhosts,0,compare_domains)
        info = {}

        alias_map= {}
        for domain, port in vhosts:
            domain_list = alias_map.get(port,[])
            domain_list.append(domain)
            alias_map[port]=domain_list
        #ok so if we have an instance_root, then we wanna sync up with the filesystem
        #otherwise, we just store it in there and count on humans to make sure it actually works
        if self.instance_root:
            zopes = [(z,z.split('_')[-1]) for z in self.zope_ids_list()]
        else:
            zopes=[]
        info['zopes'] = zopes

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
        return info



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
