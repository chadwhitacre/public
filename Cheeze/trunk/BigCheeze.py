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

from ZopeManager import ZopeManager
from ApacheVHostManager import ApacheVHostManager
from DNSManager import DNSManager

class BigCheeze(Implicit, Persistent, \
                PropertyManager, Item, \
                ZopeManager, ApacheVHostManager, DNSManager):


    security = ClassSecurityInfo()

    id = 'Cheeze'
    title = 'Centralized instance management'
    meta_type= 'Big Cheeze'

    instance_root = join(os.environ['INSTANCE_HOME'], '../')
    skel_root = ''
    apache_db = ''
    dns_file = ''

    vhosting = 0

    BigCheeze_manage_options = (
        {'label':'Zopes', 'action':'big_cheeze_edit',},
        {'label':'Domains', 'action':'big_cheeze_domains',},
        {'label':'Documentation', 'action':'big_cheeze_doc',},
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
        {'id'   :'apache_db',
         'type' :'string',
         'value':'',
         'mode': 'w',
         },
        {'id'   :'dns_file',
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
                                       __name__='big_cheeze_edit',)

    big_cheeze_domains = PageTemplateFile('www/big_cheeze_domains.pt',
                                          globals(),
                                          __name__='big_cheeze_domains',)

    big_cheeze_doc = PageTemplateFile('www/big_cheeze_doc.pt',
                                       globals(),
                                       __name__='big_cheeze_doc',)

    big_cheeze_style = DTMLFile('www/style.css',
                                globals(),
                                __name__ = 'big_cheeze_style',)

    big_cheeze_delete = ImageFile('www/delete.gif',
                                  globals(),)



    big_cheeze_edit._owner = big_cheeze_domains._owner \
                           = big_cheeze_doc._owner \
                           = big_cheeze_style._owner \
                           = big_cheeze_delete._owner \
                           = None
    manage = manage_main = big_cheeze_edit

    ##
    # helper routines
    ##

    def _setPropValue(self, id, value):
        """ intercept so we can do validation """
        if id == 'instance_root':
            self._set_instance_root(value)
        elif id == 'skel_root':
            self._set_skel_root(value)
        else:
            PropertyManager._setPropValue(self, id, value)

    def _set_instance_root(self, instance_root):
        """ validate and set the instance root """
        if instance_root == '':
            raise 'Cheeze Error', "You must enter an instance root"
        elif not os.path.exists(instance_root):
            raise 'Cheeze Error', "Proposed instance root '%s' " \
                                + "does not exist" % instance_root
        elif not os.path.isdir(instance_root):
            raise 'Cheeze Error', "Proposed instance root '%s' " \
                                + "does not point to a directory" \
                                % instance_root
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
            raise 'Cheeze Error', "Proposed skel root '%s' " \
                                + "does not exist" % skel_root
        elif not os.path.isdir(skel_root):
            raise 'Cheeze Error', "Proposed skel root '%s' " \
                                + "does not point to a directory" \
                                % skel_root
        else:
            clean_path = self._scrub_path(skel_root)
            PropertyManager._setPropValue(self, 'skel_root', clean_path)

    def _scrub_path(self, p):
        """ given a valid path, return a clean path """
        p = os.path.normpath(p)
        p = os.path.normcase(p)
        return p


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