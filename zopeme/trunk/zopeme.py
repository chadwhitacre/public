#!/usr/local/bin/python
# (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

import os, sys

ERROR = 'see man 1 zopeme for usage'

# first get and validate some options
args = sys.argv[1:]
if len(args) <> 2:
    print ERROR
else:
    sitename, port = args
    if not port.isdigit():
        print 'second argument must be a port number'
        print ERROR
    else:
        # set user, ports, & paths; make the base directory
        current_user = os.popen4('whoami')[1].read()

        http_port = int(port)
        ftp_port = http_port + 1
        zeo_port = http_port + 9

        dirname = '_'.join((sitename, port))
        root = os.path.realpath(dirname)
        client_path = os.path.join(root, 'client-1')
        server_path = os.path.join(root, 'server')

        os.makedirs(root)


        # create and configure the ZEO server instance
        os.system('/usr/local/zope/zope/bin/mkzeoinstance.py %s' % server_path)
        confile = file(os.path.join(server_path,'etc','zeo.conf'), 'r+')
        tmp = confile.read(); confile.seek(0); confile.truncate()
        tmp = tmp.replace( '  address 9999'
                         , '  address %s' % zeo_port)
        confile.write(tmp)
        confile.close()


        # create and configure the ZEO client instance
        os.system('/usr/local/zope/zope/bin/mkzopeinstance.py -d %s' % client_path)
        confile = file(os.path.join(client_path,'etc','zope.conf'), 'r+')
        tmp = confile.read(); confile.seek(0); confile.truncate()
        tmp = tmp.replace( '#    effective-user chrism'
                         , '    effective-user %s' % current_user)
        tmp = tmp.replace( '  address 8080'
                         , '  address %s' % http_port)
        tmp = tmp.replace( '  address 8021'
                         , '  address %s' % ftp_port)

        tmp = tmp.replace("""\
<zodb_db main>
    # Main FileStorage database
    <filestorage>
      path $INSTANCE/var/Data.fs
    </filestorage>
    mount-point /
</zodb_db>""", '')

        tmp = tmp.replace("""\
# <zodb_db main>
#   mount-point /
#   # ZODB cache, in number of objects
#   cache-size 5000
#   <zeoclient>
#     server localhost:8100
#     storage 1
#     name zeostorage
#     var $INSTANCE/var
#     # ZEO client cache, in bytes
#     cache-size 20MB
#     # Uncomment to have a persistent disk cache
#     #client zeo1
#   </zeoclient>
# </zodb_db>""","""\
<zodb_db main>
  mount-point /
  # ZODB cache, in number of objects
  cache-size 5000
  <zeoclient>
    server localhost:%s
    storage 1
    name zeostorage
    var $INSTANCE/var
    # ZEO client cache, in bytes
    cache-size 20MB
    # Uncomment to have a persistent disk cache
    #client zeo1
  </zeoclient>
</zodb_db>""" % zeo_port)

        confile.write(tmp)
        confile.close()



        # now install a script into rc.d
        rcd = { 'client'   : os.path.join(client_path, 'bin', 'zopectl')
              , 'server'   : os.path.join(server_path, 'bin', 'zeoctl')
              , 'name'     : dirname
              , 'fullpath' : root
               }

        rc_script = """\
#!/bin/sh -
#
#	initialization/shutdown script for the zope instance at:
#
#     %(fullpath)s

case "$1" in
start)
    %(server)s start && echo -n ' %(name)s/server' && %(client)s start && echo -n ' %(name)s/client'
    ;;
stop)
    %(client)s stop && echo -n ' %(name)s/client' && %(server)s stop && echo -n ' %(name)s/server'
    ;;
restart)
    echo -n 'restarting:'
    %(client)s stop && echo -n ' %(name)s/client' && %(server)s restart && echo -n ' %(name)s/server' && %(client)s start && echo -n ' %(name)s/client'
    echo
    ;;
*)
    echo "unknown option: $1 - should be 'start', 'stop', or 'restart'" >&2
    ;;
esac
	    """ % rcd

        rc_path = '/usr/local/zope/rc.d/%(name)s.sh' % rcd
        rc_file = file(rc_path, 'w+')
        rc_file.write(rc_script)
        rc_file.close()
        os.system('chmod 0755 %s' % rc_path)

        print 'zope+zeo instance successfully created'