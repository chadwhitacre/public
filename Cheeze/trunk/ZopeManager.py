from AccessControl import ClassSecurityInfo
import os
from os.path import join

class ZopeManager:
    """ provides functionality to manage Zope instances """

    security = ClassSecurityInfo()

    def __init__(self):
        pass


    ##
    # info providers - these can be used in mgmt zpt's
    ##

    security.declareProtected('Manage Big Cheeze', 'zopes_list',
                                                   'skel_list',
                                                   'port_get',
                                                   )

    def zope_ids_list(self):
        """ return a list of available zope instances """
        return os.listdir(self.instance_root)

    def skel_list(self):
        """ return a list of available zope skel """
        if self.skel_root == '':
            return None
        else:
            return os.listdir(self.skel_root)

    def zope_info_get(self, zope):
        """ given a zope instance, return (name, port number) """
        port = zope.split('_')[-1]
        name = ''.join(zope.split('_')[0:-1])
        return (name, port)


    ##
    # heavy lifters - these are only used by BigCheeze wrappers
    ##

    def _zope_create(self, name, skel, port):
        """ create a new zope instance """

        # initialize kw
        kw = self._initialize_kw()

        # import things
        import sys
        bin = join(kw['ZOPE_HOME'], 'bin')
        sys.path.append(bin)
        import copyzopeskel
        import mkzopeinstance

        # set skelsrc
        if skel == '|stock|':
            # default to using stock Zope skeleton source
            # NB: kw['HTTP_PORT'] will be meaningless!
            skelsrc = join(kw['ZOPE_HOME'], 'skel')
        else:
            skelsrc = join(self.skel_root, skel)

        # set port number
        if port == '':
            port = 80
        kw['HTTP_PORT'] = str(port)
        kw['FTP_PORT'] = '21' # will want to revisit this later

        # set skeltarget
        zope_id = self._zope_id_make(name,port)
        kw['INSTANCE_HOME'] = skeltarget \
                            = join(self.instance_root,zope_id)

        # now make the zope!
        copyzopeskel.copyskel(skelsrc, skeltarget, None, None, **kw)

        # and finally create the inituser
        # username:password are hardcoded for now
        inituser = join(kw['INSTANCE_HOME'], "inituser")
        mkzopeinstance.write_inituser(inituser, 'admin', 'jesus')

        # if we are vhosting then make those changes too
        # this will be moved up into BigCheeze
        #if vhosting:
        #    # this is rote from previous product
        #    zs_name = zope['name'] + zope['port'] + '.zetaserver.com'
        #    update_vhosts({zs_name:zope['port']},www=1)

    def _zope_id_set(self, old_id, new_id):
        """ rename a zope instance """

        old_path = join(self.instance_root, old_id)
        new_path = join(self.instance_root, new_id)

        # rename the directory
        # do this first since it is more failure-prone than file changes below
        os.rename(old_path, new_path)

        # update a few files
        bin = join(new_path, 'bin')
        etc = join(new_path, 'etc')

        paths =  [join(bin, fn) for fn in os.listdir(bin)]
        paths += [join(etc, fn) for fn in os.listdir(etc)]

        for path in paths:
            txt = file(path).read()
            txt = txt.replace(old_path,new_path)
            file(path, 'w').write(txt)

    def _port_set(self, zope_id, old_port):
        """ given a new zope_id and the old port number, reset the port number """

        # get the configuration file
        conf = join(self.instance_root, zope_id, 'etc/zope.conf')

        # get the new port number from the zope_id
        new_port = self.zope_info_get(zope_id)[1]

        # set the port definitions for zope.conf
        port_def = '%%define HTTP_PORT %s'
        old_port_def = port_def % old_port
        new_port_def = port_def % new_port

        # now do the replacement
        txt = file(conf).read()
        txt = txt.replace(old_port_def, new_port_def)
        file(conf, 'w').write(txt)

    def _zope_delete(self, zope):
        """ given an instance name, delete a zope """
        top = join(self.instance_root, zope)
        #raise 'top', top
        for root, dirs, files in os.walk(top, topdown=False):
            for name in files:
                os.remove(join(root, name))
            for name in dirs:
                os.rmdir(join(root, name))
        os.rmdir(top)


    ##
    # helpers
    ##

    def _zope_id_make(self, name, port):
        return '_'.join((str(name), str(port)))

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