# Zope classes we are going to subclass
from Acquisition import Implicit
from Globals import Persistent
from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import Item

# Our classes we are going to subclass
from ZopeManager import ZopeManager
from ApacheVHostManager import ApacheVHostManager
from DNSManager import DNSManager
from LocalDNSManager import LocalDNSManager

# different kinds of files
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import DTMLFile, ImageFile

# for security declarations
from AccessControl import ClassSecurityInfo

# error classes
from CheezeError import CheezeError

# utils
import os
from os.path import join
from pprint import pformat as Ipformat
from utils import *



class BigCheeze(Implicit, Persistent, \
                PropertyManager, Item, \
                ZopeManager, DNSManager,  ApacheVHostManager, LocalDNSManager):


    security = ClassSecurityInfo()

    # initialize instance metadata
    id = 'Cheeze'
    title = 'Cheap Zopes :-)'
    meta_type= 'Big Cheeze'

    # initialize mode-relevant attrs
    instance_root = vhost_db = etc_hosts = ''

    # initialize secondary attrs
    ip_list = port_list = []
    dns_file = skel_root = port_range = ''
    ips_constrain = production_mode = 0

    # initialize management tabs

    global_tabs = ({'label':'Documentation','action':'manage_doc',    },
                   {'label':'chmod',        'action':'manage_chmod',  },)
    manage_options = global_tabs \
                   + PropertyManager.manage_options \
                   + Item.manage_options

    # initialize properties
    _properties=(
        {'id'   :'title',           'type' :'string','value':'','mode': 'w',},
        {'id'   :'production_mode','type' :'boolean','value':0, 'mode': 'w',},
        {'id'   :'etc_hosts',       'type' :'string','value':'','mode': 'w',},
        {'id'   :'ip_list',         'type' :'lines', 'value':'','mode': 'w',},
        {'id'   :'vhost_db',        'type' :'string','value':'','mode': 'w',},
        {'id'   :'dns_file',        'type' :'string','value':'','mode': 'w',},
        {'id'   :'instance_root',   'type' :'string','value':'','mode': 'w',},
        {'id'   :'skel_root',       'type' :'string','value':'','mode': 'w',},
        {'id'   :'port_range',      'type' :'string','value':'','mode': 'w',},
        {'id'   :'port_list',       'type' :'lines', 'value':'','mode': 'w',},
                )

    def __init__(self, id):
        """ we are keeping instance creation simple, config after creation """
        self.id = str(id)

    ##
    #   temp
    ##
    def pformat(self,object):
        return Ipformat(object)

    dependencies = DTMLFile('doc/dependencies.txt',globals())


    ##
    # documentation
    ##

    manage_doc = PageTemplateFile('www/manage_doc.pt',globals())

    style_doc  = DTMLFile('www/style_doc.css',globals())

    def explain(self):
        """  """
        return 'Cheap Zopes :-)'


    ##
    # Host mgmt
    ##

    manage_hosts = PageTemplateFile('www/manage_hosts.pt',globals())

    def host_add(self,domain,ip):
        """ add a record to the hosts file """
        self._mapping_set(domain,ip)
        self._hosts_write()
        return self.REQUEST.RESPONSE.redirect('manage_hosts')

    def host_edit(self,domain,ip):
        """ edit the hosts file """
        self._mapping_set(domain,ip)
        self._hosts_write()
        return self.REQUEST.RESPONSE.redirect('manage_hosts')


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
        return self.REQUEST.RESPONSE.redirect('manage_domains')

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
        zopes = [(z,z.split('_')[-1]) for z in self.zope_ids_list()]
        info['zopes'] = zopes

        zope_map = dict([(zport, zname) for zname, zport in zopes])

        canon_map = dict([(zport, zname+'.zetahost.com') for zname, zport in zopes])

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
    # Zope mgmt
    ##

    manage_zopes = PageTemplateFile('www/manage_zopes.pt',globals())

    security.declareProtected('Manage Cheezen', 'zope_add'),
    def zope_add(self):
        """ add a zope instance """
        mode = self._mode
        if self.managing_zopes():
            ZopeManager._zope_add(self)
            if self.managing_domains():
                self.fs_db_sync()
        if self.managing_domains() and not self.managing_zopes():
            ApacheVHostManager._zope_add(self)
        return self.REQUEST.RESPONSE.redirect('manage_zopes')

    security.declareProtected('Manage Cheezen', 'zope_edit'),
    def zope_edit(self):
        """ edit a zope instance """
        if self.production_mode:
            raise CheezeError, 'Cannot edit instances in production mode'
        mode = self._mode
        if mode in [1,3]:
            ZopeManager._zope_edit(self)
            if mode==3:
                self.fs_db_sync()
        elif mode==2:
            ApacheVHostManager._zope_edit(self)

        return self.REQUEST.RESPONSE.redirect('manage_zopes')

    security.declareProtected('Manage Cheezen', 'zope_remove'),
    def zope_remove(self):
        """ remove a zope instance """
        mode = self._mode
        if mode in [1,3]:
            ZopeManager._zope_remove(self)
            if mode==3:
                self.fs_db_sync()
        elif mode==2:
            ApacheVHostManager._zope_remove(self)
        return self.REQUEST.RESPONSE.redirect('manage_zopes')

    def zopes_list(self):
        """ return a list of zopes for zpt """
        info = {}
        zopes = []
        mode = self._mode
        for zope_id in self.zope_ids_list():
            name, port = self.zope_info_get(zope_id)
            zope_info = {
                'name':name,
                'port':port,
                'id':zope_id,
                'canonical':zope_id+'.zetahost.com',
            }
            zopes.append(zope_info)

        return zopes

    ##
    # Property mgmt
    ##

    manage_chmod = PageTemplateFile('www/manage_chmod.pt',globals())

    # manage_chmod is not being used yet, but eventually it will replace
    # manage_propertiesForm, and we will no longer use CMF prop mgmt.
    # This is because we want more control over prop mgmt UI.

    def _setPropValue(self, id, value):
        """ intercept from PropertyManager so we can do validation """

        if type(value) == type(''):
            value = value.strip()


        # mode-relevant props

        # hosts
        if id == 'etc_hosts' and value != self.etc_hosts:
            self._etc_hosts_set(value)
            self._mode_set()

        # domains
        elif id == 'vhost_db' and value != self.vhost_db:
            self._vhost_db_set(value)
            self._mode_set()

        # zopes
        elif id == 'instance_root' and value != self.instance_root:
            self._instance_root_set(value)
            self._mode_set()


        # secondary props

        elif id == 'skel_root' and value != self.skel_root:
            self._skel_root_set(value)
            self._mode_set()
        elif id == 'port_range':
            self._set_port_range(value)
        else:
            PropertyManager._setPropValue(self, id, value)


    # mode-relevant prop setters

    def _etc_hosts_set(self, etc_hosts):
        """ validate and set the etc/hosts path """
        if etc_hosts == '':
            PropertyManager._setPropValue(self, 'etc_hosts', '')
        elif not os.path.exists(etc_hosts):
            raise CheezeError, "Proposed hosts path " \
                             + "'%s' does not exist" % etc_hosts
        elif not os.path.isfile(etc_hosts):
            raise CheezeError, "Proposed hosts path " \
                             + "'%s' " % etc_hosts \
                             + "does not point to a file"
        elif os.path.split(etc_hosts)[1] != 'hosts':
            raise CheezeError, "Proposed hosts file " \
                             + "'%s' " % os.path.split(etc_hosts)[1] \
                             + "is not named 'hosts'"
        else:
            clean_path = self._scrub_path(etc_hosts)
            PropertyManager._setPropValue(self,
                                          'etc_hosts',
                                          clean_path)

    def _vhost_db_set(self, vhost_db):
        """ validate and set the vhost db"""
        from whichdb import whichdb
        if vhost_db == '':
            PropertyManager._setPropValue(self, 'vhost_db', '')
        elif whichdb(vhost_db) is None or whichdb(vhost_db) == '':
            raise CheezeError, "vhost_db must point to a valid dbm file"
        else:
            clean_path = self._scrub_path(vhost_db)
            PropertyManager._setPropValue(self, 'vhost_db', clean_path)

    def _instance_root_set(self, instance_root):
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



    # secondary props

    def _skel_root_set(self, skel_root):
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
        """ validate and set the port range """
        if port_range == '':
            PropertyManager._setPropValue(self, 'port_range', '')
        else:
            self._ports_list(port_range) # smoke it!
            PropertyManager._setPropValue(self, 'port_range', port_range)



    # props helper

    def _scrub_path(self, p):
        """ given a valid path, return a clean path """
        p = os.path.normpath(p)
        p = os.path.normcase(p)
        return p



    ##
    # Mode mgmt
    ##

    _mode = 0

    security.declareProtected('Manage Cheezen','managing_host',
                                               'managing_domains',
                                               'managing_zopes',)

    def managing_hosts(self):
        return self._mode in [1,3,5,7]

    def managing_domains(self):
        return self._mode in [2,3,6,7]

    def managing_zopes(self):
        return self._mode in [4,5,6,7]

    def _mode_set(self):
        """ set the mode of the Cheeze instance, based on its props """

        managesHosts = self.etc_hosts
        managesDomains = self.vhost_db
        managesZopes   = self.instance_root

        # set the mode

        if not(managesHosts or managesDomains or managesZopes):
            self._mode = 0
        elif managesHosts and not (managesDomains or managesZopes):
            self._mode = 1
        elif not managesHosts and managesDomains and not managesZopes:
            self._mode = 2
        elif managesHosts and managesDomains and not managesZopes:
            self._mode = 3
        elif not (managesHosts or managesDomains) and managesZopes:
            self._mode = 4
        elif managesHosts and not managesDomains and managesZopes:
            self._mode = 5
        elif not managesHosts and managesDomains and managesZopes:
            self._mode = 6
        elif managesHosts and managesDomains and managesZopes:
            self._mode = 7


        # and update the management tabs

        mode = self._mode

        hosts_tab   = {'label':'Hosts',  'action':'manage_hosts',}
        if self.managing_hosts() and self.managing_domains():
            hosts_tab['label'] = 'Servers'
        elif self.managing_hosts() and not self.managing_domains():
            hosts_tab['label'] = 'Local DNS'
        domains_tab = {'label':'Domains','action':'manage_domains',}
        zopes_tab   = {'label':'Zopes',  'action':'manage_zopes',  }

        tabs = list(self.manage_options)

        # first take out all the ones we don't want

        for tab in tabs:
            if (tab['action'] == hosts_tab['action']) and not self.managing_hosts():
                tabs.remove(hosts_tab)
            elif (tab == domains_tab) and not self.managing_domains():
                tabs.remove(domains_tab)
            elif (tab == zopes_tab) and not self.managing_zopes():
                tabs.remove(zopes_tab)

        # and then add the ones we do want back on the front

        if self.managing_hosts() and hosts_tab not in tabs:
            tabs.insert(0, hosts_tab)
        if self.managing_domains() and domains_tab not in tabs:
            tabs.insert(0, domains_tab)
        if self.managing_zopes() and zopes_tab not in tabs:
            tabs.insert(0, zopes_tab)

        self.manage_options = tuple(tabs)


    ##
    # presentation helpers
    ##

    style           = DTMLFile('www/style.css',globals())

    image_delete    = ImageFile('www/delete.png',globals(),)

    image_save      = ImageFile('www/save.png',globals(),)

    image_star      = ImageFile('www/star.png',globals(),)

    image_zopes     = ImageFile('www/zopes.png',globals(),)

    #manage = manage_main = manage_workspace

    regex_default = 'regex filter goes here'

    def filter_set(self, name, regex):
        """ given a name and a regex, set a filter as a cookie """
        cookie_name = '_'.join(['cheeze',name,'filter'])
        self._cookie_set(cookie_name, regex)

    def filter_get(self, name):
        """ given a name, return a regex from a cookie """

        cookie_name = '_'.join(['cheeze',name,'filter'])
        regex = self._cookie_get(cookie_name)

        if regex == '':
            regex = self.regex_default
        return regex

    ##
    # Yummy cookies
    ##

    def _cookie_set(self, name, value, expires='Wed, 19 Feb 2020 14:28:00 GMT'):
        """ sets an arbitrary cookie """
        # I suppose this could be used to maliciously set a cookie
        # but then there would be no way to get the cookie so I
        # guess it's not dangerous
        r = self.REQUEST
        rr = r.RESPONSE
        rr.setCookie(name, value.strip(), expires=expires)
        rr.redirect(r['HTTP_REFERER'])

    def _cookie_get(self, name):
        """ gets an arbitrary a cookie """
        return self.REQUEST.cookies.get(name,'')


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
