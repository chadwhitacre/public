from Products.Cheeze.interfaces.BigCheeze import IBigCheeze
try:
    from Products.Cheeze.vh_utils import update_vhosts, \
                                         recreate_vhosts, \
                                         get_vhosts
    vhosting = 1
except:
    # we are not on unix :/
    vhosting = 0
from Products.ZetaUtils import compare_domains, pformat, index_sort
from AccessControl import ClassSecurityInfo

from Acquisition import Implicit
from Globals import Persistent
from AccessControl.Role import RoleManager
from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import Item

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import DTMLFile
import os


class BigCheeze(Implicit, Persistent, \
                RoleManager, PropertyManager, Item,):

    __implements__ = IBigCheeze

    security = ClassSecurityInfo()

    id = 'Cheeze'
    title = 'Centralized instance management'
    meta_type= 'Big Cheeze'
    instance_root = ''
    skel_root = ''

    BigCheeze_manage_options = (
        {'label':'Edit', 'action':'big_cheeze_edit',
         'help': ('Cheeze', 'Big_Cheeze_Edit.stx')},
        )


    manage_options = BigCheeze_manage_options \
                   + PropertyManager.manage_options \
                   + RoleManager.manage_options \
                   + Item.manage_options

    _properties=(
        {'id'   :'instance_root',
         'type' :'string',
         'value':'',
         'mode': 'w',
         },
        {'id'   :'skel_root',
         'type' :'string',
         'value':'',
         'mode': 'w',
         },
                )

    def __init__(self, id, instance_root='', skel_root=''):
        self.id = str(id)
        self._set_instance_root(str(instance_root))
        self._set_skel_root(str(skel_root))

    big_cheeze_edit = PageTemplateFile('www/big_cheeze_edit.pt', globals(),
                                       __name__='big_cheeze_edit')
    big_cheeze_edit._owner = None
    manage = manage_main = big_cheeze_edit

    big_cheeze_style = DTMLFile('www/style.css', globals(),
                                __name__ = 'big_cheeze_style',
                                  )
    big_cheeze_edit._owner = None


    ##
    # helper routines
    ##

    def _setPropValue(self, id, value):
        """ override PropertyManager default in order to provide validation """
        if id == 'instance_root':
            self._set_instance_root(value)
        elif id == 'skel_root':
            self._set_skel_root(value)
        else:
            PropertyManager._setPropValue(self, id, value)

    def _set_instance_root(self, instance_root):
        """ validate and set the instance root """
        if os.path.exists(instance_root):
            if os.path.isdir(instance_root):
                clean_path = self._scrub_path(instance_root)
                PropertyManager._setPropValue(self,
                                              'instance_root',
                                              clean_path)
            else:
                raise 'Cheeze Error', "Proposed instance root '%s' " \
                                    + "does not point to a directory" \
                                    % instance_root
        else:
            raise 'Cheeze Error', "Proposed instance root '%s' " \
                                + "does not exist" % instance_root

    def _set_skel_root(self, skel_root):
        """ validate and set the skel root """
        if os.path.exists(skel_root):
            if os.path.isdir(skel_root):
                clean_path = self._scrub_path(skel_root)
                PropertyManager._setPropValue(self,
                                              'skel_root',
                                              clean_path)
            else:
                raise 'Cheeze Error', "Proposed skel root '%s' " \
                                    + "does not point to a directory" \
                                    % skel_root
        else:
            raise 'Cheeze Error', "Proposed skel root '%s' " \
                                + "does not exist" % skel_root

    def _scrub_path(self, p):
        """ given a valid path, return a clean path """
        p = os.path.normcase(p)
        p = os.path.normpath(p)
        return p

    def _list_zopes(self):
        """ return a list of available zope instances """

        # get a directory listing of the instance root!

        return os.listdir(self.instance_root)



    ##
    # Helpers for the zopes pt
    ##

    security.declareProtected('zopes_info','Manage Big Cheeze')
    def zopes_info(self, troubleshoot=0):
        "populate the zopes pt"
        avail_ports = [str(x) for x in range(8010,9000,10)]
        zopes = self._list_zopes()
        index_sort(zopes,0,cmp)
        for name, port in zopes:
            if port in avail_ports:
                avail_ports.remove(port)
        info={
        'avail_ports':avail_ports,
        'zopes':zopes,
        }
        return info

    security.declareProtected('zopes_process','Manage Big Cheeze'),
    def zopes_process(self):
        "this processes the zopes pt"
        request = self.REQUEST
        response = request.RESPONSE
        form = request.form
        zope = form['zope']
        if zope['name']:
            zs_name = zope['name'] + zope['port'] + '.zetaserver.com'
            update_vhosts({zs_name:zope['port']},www=1)
        return response.redirect('zopes')

    ##
    # vhost wrappers
    ##

    def waxit(self):
        "clear out the vhosts"
        recreate_vhosts({})
        return 'waxed'

    def delete_vhosts(self, vhostname):
        "deletes a vhost given a name"
        request = self.REQUEST
        response = request.RESPONSE
        from Products.ZetaServerAdmin import delete_vhost

        delete_vhost(vhostname)

        return response.redirect(request.HTTP_REFERER)


    ##
    # Helpers for the domains pt
    ##

    def domains_info(self, troubleshoot=0):
        "populates the domains pt"
        vhosts = self.domains_list()
        index_sort(vhosts,0,compare_domains)
        info = {}
        info['vhosts'] = vhosts
        server_info = {}
        for domain, server in vhosts:
            domain_list = server_info.get(server,[])
            domain_list.append(domain)
            server_info[server]=domain_list
        info['servers'] = server_info
        if troubleshoot:
            print pformat(info)
            return printed
        else:
            return info

    def domains_list(self):
        "list the available domains"
        from Products.ZetaServerAdmin import get_vhosts
        vhosts = get_vhosts().items()
        domains = []
        print 'hey'
        for vhost in vhosts:
            name, port = vhost
            pattern = '0.zetaserver.com'
            if not name.count(pattern):
                domains.append(vhost)
        return domains





##
# Product addition and registration
##

manage_addBigCheezeForm = PageTemplateFile(
    'www/big_cheeze_add.pt', globals(), __name__='manage_addBigCheezeForm')

def manage_addBigCheeze(self, id, instance_root='', skel_root='', REQUEST=None):
    """ """
    self._setObject(id, BigCheeze(id, instance_root, skel_root))

    # prolly should check to see if the instance and skel roots exist
    # and return an error if they don't

    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)




def initialize(context):
    context.registerClass(
        BigCheeze,
        permission='Add Big Cheeze',
        constructors=(manage_addBigCheezeForm,
                      manage_addBigCheeze),
        icon='www/big_cheeze.png',
        )
    context.registerHelp()
    context.registerHelpTitle('Cheeze')