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
from Globals import DTMLFile, ImageFile
import os
from os.path import join


class BigCheeze(Implicit, Persistent, \
                RoleManager, PropertyManager, Item,):

    __implements__ = IBigCheeze

    security = ClassSecurityInfo()

    id = 'Cheeze'
    title = 'Centralized instance management'
    meta_type= 'Big Cheeze'
    instance_root = join(os.environ['INSTANCE_HOME'], '../')
    skel_root = ''
    vhosting = 0

    BigCheeze_manage_options = (
        {'label':'Zopes', 'action':'big_cheeze_edit',},
        {'label':'Domains', 'action':'big_cheeze_domains',},
        {'label':'Documenttion', 'action':'big_cheeze_doc',},
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
        """ given a zope instance, return its port number """
        if vhosting:
            pass
        else:
            return None


    ##
    # zope instance managment routines
    ##

    security.declareProtected('Manage Big Cheeze', 'create_zope'),
    def create_zope(self):
        """ create a new zope instance """
        request = self.REQUEST
        response = request.RESPONSE
        form = request.form
        zope = form['zope']
        if zope['name'] != '':
            # we are ready to rock!!!

            # import things
            import copyzopeskel
            import mkzopeinstance

            # initialize kw
            kw = self._initialize_kw()

            # set skelsrc
            skel = zope['skel']
            if skel == '|stock|':
                # default to using stock Zope skeleton source
                # NB: kw['HTTP_PORT'] will be meaningless!
                skelsrc = join(kw['ZOPE_HOME'], 'skel')
            else:
                skelsrc = join(self.skel_root, skel)

            # set skeltarget
            kw['INSTANCE_HOME'] = skeltarget \
                                = join(self.instance_root,
                                               zope['name'])

            # set port number
            port = zope['port'] # we will only get a port if vhosting is true
            if port == '':
                port = '80'
            kw['HTTP_PORT'] = port
            kw['FTP_PORT'] = '21' # will want to revisit this later

            # now make the zope!
            copyzopeskel.copyskel(skelsrc, skeltarget, None, None, **kw)

            # and finally create the inituser
            # username:password are hardcoded for now
            inituser = join(kw['INSTANCE_HOME'], "inituser")
            mkzopeinstance.write_inituser(inituser, 'admin', 'jesus')

            # if we are vhosting then make those changes to
            if vhosting:
                # this is rote from previous product
                zs_name = zope['name'] + zope['port'] + '.zetaserver.com'
                update_vhosts({zs_name:zope['port']},www=1)
        else:
            raise 'Cheeze Error', 'Please enter the name of the Zope to create'
        return response.redirect('manage')


    security.declareProtected('Manage Big Cheeze', 'delete_zope'),
    def delete_zope(self, zope):
        """ given an instance name, delete a zope """
        top = join(self.instance_root, zope)
        #raise 'top', top
        for root, dirs, files in os.walk(top, topdown=False):
            for name in files:
                os.remove(join(root, name))
            for name in dirs:
                os.rmdir(join(root, name))
        os.rmdir(top)
        return self.REQUEST.RESPONSE.redirect('manage')

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

    def _initialize_kw(self):
        """ return initial kw for use in copyzopeskel """
        import sys

        ### BEGIN COPY FROM mkzopeinstance.py ###

        # we need to distinguish between python.exe and pythonw.exe under
        # Windows in order to make Zope run using python.exe when run in a
        # console window and pythonw.exe when run as a service, so we do a bit
        # of sniffing here.
        psplit = os.path.split(sys.executable)
        exedir = join(*psplit[:-1])
        pythonexe = join(exedir, 'python.exe')
        pythonwexe = join(exedir, 'pythonw.exe')

        if ( os.path.isfile(pythonwexe) and os.path.isfile(pythonexe) and
             (sys.executable in [pythonwexe, pythonexe]) ):
            # we're using a Windows build with both python.exe and pythonw.exe
            # in the same directory
            PYTHON = pythonexe
            PYTHONW = pythonwexe
        else:
            # we're on UNIX or we have a nonstandard Windows setup
            PYTHON = PYTHONW = sys.executable

        ### END COPY FROM mkzopeinstance.py ###

        softwarehome = os.environ.get('SOFTWARE_HOME', '')
        zopehome     = os.environ.get('ZOPE_HOME', '')

        return {"PYTHON"        : PYTHON,
                "PYTHONW"       : PYTHONW,
                "SOFTWARE_HOME" : softwarehome,
                "ZOPE_HOME"     : zopehome,
                }


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