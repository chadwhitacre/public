from AccessControl import ClassSecurityInfo
import os
from os.path import join

class ZopeManager:
    """ provides functionality to manage Zope instances """

    security = ClassSecurityInfo()

    def __init__(self):
        pass


    ##
    # info providers
    ##

    security.declareProtected('Manage Big Cheeze', 'list_zopes',
                                                   'list_skel',
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

    def get_port(self, zope):
        """ given a zope instance, return its port number """
        return None


    ##
    # heavy lifters
    ##

    security.declareProtected('Manage Big Cheeze', 'zope_create'),
    def zope_create(self):
        """ create a new zope instance """
        request = self.REQUEST
        response = request.RESPONSE
        form = request.form
        zope = form['zope']
        if zope['name'] != '':
            # we are ready to rock!!!

            # initialize kw
            kw = self._initialize_kw()

            # import things
            import sys
            bin = join(kw['ZOPE_HOME'], 'bin')
            sys.path.append(bin)
            import copyzopeskel
            import mkzopeinstance

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
            port = zope['port']
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

            # if we are vhosting then make those changes too
            if vhosting:
                # this is rote from previous product
                zs_name = zope['name'] + zope['port'] + '.zetaserver.com'
                update_vhosts({zs_name:zope['port']},www=1)
        else:
            raise 'Cheeze Error', 'Please enter the name of the Zope to create'
        return response.redirect('manage')


    security.declareProtected('Manage Big Cheeze', 'zope_delete'),
    def zope_delete(self, zope):
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
    # helpers
    ##

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
