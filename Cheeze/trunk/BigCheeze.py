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
    vhosting = 0

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

    ##
    # These are attributes that we will call TTW for manage views
    ##

    big_cheeze_edit = PageTemplateFile('www/big_cheeze_edit.pt',
                                       globals(),
                                       __name__='big_cheeze_edit')
    big_cheeze_edit._owner = None
    manage = manage_main = big_cheeze_edit

    big_cheeze_style = DTMLFile('www/style.css',
                                globals(),
                                __name__ = 'big_cheeze_style',
                                  )
    big_cheeze_edit._owner = None

#    big_cheeze_delete = ImageFile('www/delete.gif',
#                                globals(),
#                                __name__ = 'big_cheeze_delete',
#                                  )
#    big_cheeze_delete._owner = None



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
        if skel_root == '':
            PropertyManager._setPropValue(self,
                                          'skel_root',
                                          skel_root)
        elif os.path.exists(skel_root):
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


    ##
    # info providers
    ##
    security.declareProtected('Manage Big Cheeze', 'list_zopes',
                                                   'list_skel',
                                                   'list_ports',
                                                   'get_port',
                                                   )

    def list_zopes(self):
        """ return a list of available zope instances """
        return os.listdir(self.instance_root)

    def list_skel(self):
        """ return a list of available zope skel """
        if self.skel_root == '':
            return None
        else:
            return os.listdir(self.skel_root)

    def list_ports(self):
        """ return a list of available ports """
        if vhosting:
            avail_ports = [str(x) for x in range(8010,9000,10)]
            for zope in self.list_zopes():
                if self.get_port(zope) in avail_ports:
                    avail_ports.remove(port)
        else:
            return None

    def get_port(self, zope):
        """ given a zope instance return its port number """
        if vhosting:
            pass
        else:
            return None


    ##
    # zope instance managment routines
    ##

    security.declareProtected('zopes_process','Manage Big Cheeze'),
    def create_zope(self):
        """ create a new zope instance """
        request = self.REQUEST
        response = request.RESPONSE
        form = request.form
        zope = form['zope']
        if zope['name']:
            zs_name = zope['name'] + zope['port'] + '.zetaserver.com'
            update_vhosts({zs_name:zope['port']},www=1)
        return response.redirect('manage')

#    security.declareProtected('zopes_process','Manage Big Cheeze'),
#    def zopes_process(self):
#        "this processes the zopes pt"
#        request = self.REQUEST
#        response = request.RESPONSE
#        form = request.form
#        zope = form['zope']
#        if zope['name']:
#            zs_name = zope['name'] + zope['port'] + '.zetaserver.com'
#            update_vhosts({zs_name:zope['port']},www=1)
#        return response.redirect('zopes')






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